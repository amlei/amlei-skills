#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSDN 文章发布器（Playwright + CDP，复用已登录的浏览器会话）。

设计要点：
- 不重开登录、不碰账号密码。通过 CDP 连接你"已经登录好 CSDN"的浏览器（任一 Chromium 内核），
  在现有浏览器里开一个新标签页驱动 https://editor.csdn.net/md/ 编辑器。
- 正文用编辑器自带的"导入 Markdown"隐藏文件输入（#import-markdown-file-input）
  灌入——比剪贴板粘贴可靠；CSDN 会把"文件名"当作文章标题，所以把临时文件命名为标题即可。
- 正文最前默认插 @[toc]，CSDN 据各级标题自动生成可点击目录。
- 元数据（标签/摘要/分类专栏/可见范围）从 md 的 YAML front matter 读，命令行可覆盖。
- 发布是"对外、难撤回"的动作：默认填完后【暂停等你确认】再点最终发布，
  用 --auto-publish / --yes 跳过，--dry-run 只填不发。

前置：
  pip install playwright pyperclip
  用你日常、已登录 CSDN 的 Chromium 内核浏览器（Chrome/Edge/Brave/Arc/Vivaldi 等）即可——无需拷贝 profile。

开启浏览器调试（每次重启浏览器后需重新开启）：
  Chrome/Edge 136+ 禁止在默认 profile 上用 --remote-debugging-port 命令行参数。
  正解：在你要用的浏览器里打开 edge://inspect/#remote-debugging（Chrome 用 chrome://inspect），
  勾选「Allow remote debugging for this browser instance」。
  脚本会从 DevToolsActivePort 读出 WS 端点、直连该浏览器——绕过被屏蔽的 HTTP /json/version，
  复用你现成的 CSDN 登录态，无需拷贝 profile、无需重登。

退出码：0 成功；2 连不上 CDP / 找不到文件；3 未登录/页面异常；4 发布步骤出错。
"""

import argparse
import json
import os
import re
import sys
import tempfile

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    sys.stderr.write("缺少 playwright，请先安装：pip install playwright pyperclip\n")
    sys.exit(2)

EDITOR_URL = "https://editor.csdn.net/md/"

# 选择器（本文件是唯一事实源）。CSDN 改版会让其中一些失效——
# F12 开 DevTools 重新定位（找 id/placeholder/class 片段），改下面 SEL 对应项即可。
SEL = {
    "editor_body": ".editor__inner",                     # contenteditable <pre>，正文
    "import_input": "#import-markdown-file-input",       # 导入 md 的隐藏 file input
    "open_dialog": 'xpath=//button[contains(@class,"btn-publish") and normalize-space(text())="发布文章"]',
    "modal": ".modal__publish-article",
    "add_tag": 'xpath=//div[contains(@class,"mark_selection")]//button[contains(@class,"tag__btn-tag") and contains(text(),"添加文章标签")]',
    "tag_input": ".mark_selection_box .el-input__inner",
    "tag_close": 'xpath=//div[contains(@class,"mark_selection_box")]//button[@title="关闭"]',
    "summary": ".desc-box textarea",
    "cover_input": 'xpath=//div[contains(@class,"modal__publish-article")]//input[contains(@class,"el-upload__input") and @type="file"]',
    "final_publish": 'xpath=//div[contains(@class,"modal__publish-article")]//button[contains(@class,"btn-b-red") and normalize-space(text())="发布文章"]',
}
# 在弹窗内按可见文本点选（专栏项、可见范围项都用这个）
def text_in_modal_xpath(text):
    safe = text.replace('"', '\\"')
    return f'xpath=//div[contains(@class,"modal__publish-article")]//*[normalize-space(text())="{safe}"]'


# ----------------------------- front matter 解析 -----------------------------
def parse_front_matter(text):
    fm, body = {}, text
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return fm, body
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return fm, body
    body = "\n".join(lines[end + 1:])
    key = None
    for ln in lines[1:end]:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", s)
        if m:
            key = m.group(1).lower()
            val = m.group(2).strip()
            if val == "":
                fm[key] = []
            elif val.startswith("[") and val.endswith("]"):
                fm[key] = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
            elif val.lower() in ("true", "false"):
                fm[key] = val.lower() == "true"
            else:
                fm[key] = val.strip("\"'")
        elif s.startswith("- ") and key:
            fm.setdefault(key, [])
            if isinstance(fm[key], list):
                fm[key].append(s[2:].strip().strip("\"'"))
    return fm, body


def ensure_toc(body):
    if re.search(r"(?m)^\s*@\[TOC\]\s*$", body, re.I):
        return body
    return "@[toc]\n\n" + body.lstrip("\n")


def safe_filename(title):
    return re.sub(r'[\\/:\*\?"<>\|]', "_", title).strip()[:100] or "untitled"


def probe_text(body):
    m = re.search(r"(?m)^\s{0,3}#{1,6}\s+(.+)$", body)
    return (m.group(1).strip() if m else body.strip()[:24])


# ----------------------------- 主流程 -----------------------------
def open_editor_and_login(page, login_wait):
    page.goto(EDITOR_URL, wait_until="domcontentloaded")
    try:
        page.wait_for_selector(SEL["editor_body"], state="attached", timeout=login_wait * 1000)
    except PWTimeout:
        sys.stderr.write(f"[error] {login_wait}s 内未进入编辑器。请在连接的浏览器里登录 CSDN 后重试。\n")
        sys.exit(3)
    page.wait_for_timeout(2500)
    if "/login" in page.url or "passport.csdn.net" in page.url:
        sys.stderr.write("[error] 未登录 CSDN，请在连接的浏览器里登录后重试。\n")
        sys.exit(3)


def load_body_via_import(page, title, body):
    """用 #import-markdown-file-input 导入临时 md：正文灌入，标题取自文件名。"""
    fname = safe_filename(title) + ".md"
    tmpdir = tempfile.mkdtemp(prefix="csdn_post_")
    tmp = os.path.join(tmpdir, fname)  # 文件名=标题，CSDN 会去掉 .md 后缀当标题
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(body)
    try:
        page.locator(SEL["import_input"]).set_input_files(tmp)
    finally:
        try:
            os.remove(tmp); os.rmdir(tmpdir)
        except OSError:
            pass
    page.wait_for_timeout(2500)
    got = page.evaluate("() => { const e=document.querySelector('.editor__inner'); return e?(e.innerText||e.textContent||''):''; }")
    probe = probe_text(body)
    if probe and probe not in got:
        sys.stderr.write(f"[warn] 导入后正文里没找到探针「{probe}」，可能没灌进去；请到浏览器核对。\n")
    disp = page.evaluate("() => (document.querySelector('.article-bar__title-display')||{}).innerText || ''")
    return disp.strip()


def open_dialog(page):
    page.locator(SEL["open_dialog"]).first.click()
    page.wait_for_selector(SEL["modal"], state="visible", timeout=15000)
    page.wait_for_timeout(1200)


def add_tags(page, tags):
    try:
        page.locator(SEL["add_tag"]).first.click()
        page.wait_for_timeout(900)
        tin = page.locator(SEL["tag_input"])
        tin.wait_for(state="visible", timeout=10000)
        for t in tags:
            tin.fill(str(t))
            page.wait_for_timeout(1500)
            tin.press("Enter")
            page.wait_for_timeout(800)
        try:
            page.locator(SEL["tag_close"]).click(timeout=4000)
        except Exception:
            page.keyboard.press("Escape")
    except Exception as e:
        sys.stderr.write(f"[warn] 标签填写异常：{e}\n")


def set_summary(page, summary):
    try:
        ta = page.locator(SEL["summary"])
        ta.wait_for(state="visible", timeout=10000)
        ta.fill(str(summary))
        page.wait_for_timeout(500)
    except Exception as e:
        sys.stderr.write(f"[warn] 摘要填写异常：{e}\n")


def set_cover(page, cover):
    local = download_if_url(cover)
    if not local or not os.path.exists(local):
        sys.stderr.write(f"[warn] 封面不可用：{cover}\n"); return
    try:
        page.locator(SEL["cover_input"]).first.set_input_files(local)
        page.wait_for_timeout(1500)
    except Exception as e:
        sys.stderr.write(f"[warn] 封面设置失败（不影响发布，CSDN 会自动取正文首图）：{e}\n")


def click_text_in_modal(page, text, timeout=6000, force=False):
    loc = page.locator(text_in_modal_xpath(text))
    try:
        loc.first.wait_for(state="attached", timeout=timeout)
        loc.first.click(timeout=timeout, force=force)
        return True
    except Exception as e:
        sys.stderr.write(f"[warn] 点选「{text}」失败：{e}\n")
        return False


def select_columns(page, cols):
    # 1. 打开专栏选择面板（按钮文字是"新建分类专栏"，点开后会列出已有专栏）
    try:
        page.locator('xpath=//button[contains(@class,"tag__btn-tag") and contains(text(),"新建分类专栏")]').first.click(timeout=8000)
    except Exception as e:
        sys.stderr.write(f"[warn] 打不开分类专栏选择器：{e}\n")
        return
    # 等专栏 label 加载（面板有异步 loading 遮罩，等它出列再点）
    try:
        page.wait_for_selector(".tag__options-content .tag__option-label", state="attached", timeout=10000)
    except PWTimeout:
        sys.stderr.write("[warn] 分类专栏列表没加载出来\n")
        page.keyboard.press("Escape")
        return
    page.wait_for_timeout(800)
    # 2. JS 直接点 label 关联的 input（绕过 loading 遮罩的 pointer 拦截）
    for col in cols:
        clicked = page.evaluate(
            r"""(name) => {
                const el = Array.from(document.querySelectorAll('.tag__options-content .tag__option-label'))
                    .find(e => (e.innerText||'').trim() === name);
                if (!el) return '';
                const inp = el.querySelector('input');
                if (inp) { inp.click(); return 'input'; }
                el.click(); return 'label';
            }""",
            str(col),
        )
        if not clicked:
            sys.stderr.write(f"[warn] 没有匹配的分类专栏「{col}」（用 --list-columns 看真实名称）\n")
        else:
            page.wait_for_timeout(400)
    # 3. 关闭面板
    try:
        page.locator('xpath=//div[contains(@class,"tag__options-content")]//button[contains(@class,"modal__close-button")]').first.click(timeout=4000)
    except Exception:
        page.keyboard.press("Escape")


def set_visibility(page, vis):
    # 仅我可见=私密；全部可见=公开；粉丝可见；VIP可见。JS 点 input 绕过遮罩。
    clicked = page.evaluate(
        r"""(vis) => {
            const el = Array.from(document.querySelectorAll('.modal__publish-article .lab-switch'))
                .find(e => (e.innerText||'').trim() === vis);
            if (!el) return '';
            const inp = el.querySelector('input') || (el.getAttribute('for') ? document.getElementById(el.getAttribute('for')) : null);
            if (inp) { inp.click(); return 'input'; }
            el.click(); return 'label';
        }""",
        vis,
    )
    if not clicked:
        sys.stderr.write(f"[warn] 找不到可见范围选项「{vis}」，保持默认。\n")


def verify_dialog(page):
    """打印发布弹窗当前的关键字段状态，供核验。"""
    try:
        return page.evaluate(r"""() => {
          const q = s => document.querySelector(s);
          // 可见范围：每个"可见"label 的 for 指向兄弟 radio，看哪个 checked
          let vis = '(none)';
          for (const lab of Array.from(document.querySelectorAll('.modal__publish-article .lab-switch')).filter(e => /可见/.test(e.innerText))) {
            const forId = lab.getAttribute('for');
            const inp = forId && document.getElementById(forId);
            if (inp && inp.checked) { vis = (lab.innerText||'').trim(); break; }
          }
          // 已选专栏：tag__box 里除"新建分类专栏"按钮外的文本即已选专栏 chip
          const tagBox = (q('.modal__publish-article .tag__box')||{}).innerText?.replace(/\s+/g,' ').trim() || '';
          const cols = tagBox.replace('新建分类专栏','').trim();
          return {
            summary: (q('.desc-box textarea')||{}).value || '',
            tagsText: (q('.mark_selection')||{}).innerText?.replace(/\s+/g,' ').trim().slice(0,120) || '',
            selectedColumns: cols ? cols.split(/\s{2,}|\s+/).filter(Boolean) : [],
            visibility: vis,
          };
        }""")
    except Exception as e:
        return {"verify_error": str(e)}


def list_columns(page):
    """打开发布弹窗→打开专栏选择面板，列出已有专栏名称后退出。"""
    open_editor_and_login(page, 120)
    open_dialog(page)
    try:
        page.locator('xpath=//button[contains(@class,"tag__btn-tag") and contains(text(),"新建分类专栏")]').first.click(timeout=8000)
        page.wait_for_timeout(1500)
    except Exception as e:
        sys.stderr.write(f"[error] 打不开分类专栏选择器：{e}\n")
    cols = page.evaluate(
        r"""() => Array.from(document.querySelectorAll('.tag__options-content .tag__option-label'))
            .map(e=>(e.innerText||'').trim()).filter(Boolean)"""
    )
    print(json.dumps(cols, ensure_ascii=False, indent=2))


def publish_and_get_url(page, auto_publish):
    if not auto_publish:
        sys.stdout.write(
            "\n>>> 元数据已填好，请在浏览器里核对发布弹窗。\n"
            "    回车=点「发布文章」正式发布；Ctrl-C=中止（弹窗留在浏览器里供手动发）。\n"
        )
        try:
            input()
        except KeyboardInterrupt:
            sys.stdout.write("已中止，未发布。\n"); return None
    try:
        page.locator(SEL["final_publish"]).first.click(timeout=10000)
    except Exception as e:
        sys.stderr.write(f"[error] 点击最终发布失败：{e}\n"); sys.exit(4)
    url = None
    for _ in range(25):
        page.wait_for_timeout(1000)
        cur = page.url
        if "/article/details/" in cur:
            url = cur; break
        try:
            href = page.locator("xpath=//a[contains(@href,'/article/details/')]").first.get_attribute("href", timeout=1500)
            if href:
                url = href if href.startswith("http") else "https://blog.csdn.net" + href
                break
        except Exception:
            pass
    return url or page.url


# ----------------------------- 杂项 -----------------------------
def download_if_url(cover):
    if not str(cover).startswith(("http://", "https://")):
        return cover
    import urllib.request
    try:
        suffix = os.path.splitext(re.split(r"[?#]", cover)[0])[1] or ".png"
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        urllib.request.urlretrieve(cover, path)
        return path
    except Exception as e:
        sys.stderr.write(f"[warn] 下载封面失败：{e}\n"); return None


def devtools_ws_endpoint():
    """从已开启调试的 Chromium 浏览器（Chrome/Edge/Brave/Arc/Vivaldi 等）的
    DevToolsActivePort 读出 WS 端点。直连 WS 可绕过 Chrome 136 对默认 profile
    屏蔽的 HTTP /json/version。自动探测各浏览器的 profile 目录。"""
    home = os.path.expanduser("~")
    candidates = [
        # macOS
        "Library/Application Support/Google/Chrome",
        "Library/Application Support/Microsoft Edge",
        "Library/Application Support/BraveSoftware/Brave-Browser",
        "Library/Application Support/Arc/User Data",
        "Library/Application Support/Vivaldi",
        "Library/Application Support/Chromium",
        # Linux
        ".config/google-chrome",
        ".config/microsoft-edge",
        ".config/BraveSoftware/Brave-Browser",
        ".config/vivaldi",
        ".config/chromium",
    ]
    for rel in candidates:
        try:
            with open(os.path.join(home, rel, "DevToolsActivePort"), encoding="utf-8") as fh:
                lines = fh.read().splitlines()
            port, path = lines[0].strip(), lines[1].strip()
            if port.isdigit() and path.startswith("/"):
                return f"ws://127.0.0.1:{port}{path}"
        except Exception:
            continue
    return None


def connect(cdp_url):
    endpoint = cdp_url or devtools_ws_endpoint()
    if not endpoint:
        sys.stderr.write(
            "[error] 没找到可连接的浏览器调试端点。\n"
            "请在你的 Chromium 浏览器（Chrome/Edge/Brave/Arc/Vivaldi 等）打开\n"
            "  <浏览器>://inspect/#remote-debugging（如 edge://inspect、chrome://inspect、brave://inspect），\n"
            "勾选「Allow remote debugging for this browser instance」后重跑。\n"
            "（无需拷贝 profile；脚本通过 DevToolsActivePort 直连你已登录的浏览器。）\n"
        )
        sys.exit(2)
    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(endpoint)
    except Exception as e:
        pw.stop()
        sys.stderr.write(
            f"[error] 连不上浏览器 CDP（{endpoint}）：{e}\n"
            "确认已在 edge://inspect/#remote-debugging 勾选「Allow remote debugging for this browser instance」。\n"
        )
        sys.exit(2)
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    return pw, browser, ctx


def main():
    ap = argparse.ArgumentParser(description="把 md 发布到 CSDN（复用已登录的浏览器）")
    ap.add_argument("md", nargs="?", help="要发布的 Markdown 文件路径")
    ap.add_argument("--cdp-url", default=None, help="CDP 端点（ws://... 或 http://...）；默认从 DevToolsActivePort 自动发现已开调试的 Chrome/Edge")
    ap.add_argument("--title", help="文章标题（覆盖 front matter；用作导入文件名）")
    ap.add_argument("--tag", action="append", help="标签，可多次；覆盖 front matter")
    ap.add_argument("--column", action="append", help="分类专栏名称（弹窗里点选，须账号已有）")
    ap.add_argument("--summary", help="摘要")
    ap.add_argument("--cover", help="封面图片本地路径或 URL")
    ap.add_argument("--visibility", default="全部可见", help="全部可见/仅我可见/粉丝可见/VIP可见，默认「全部可见」(公开)")
    ap.add_argument("--toc", dest="toc", action="store_true", default=True, help="正文开头插 @[toc] 目录（默认开）")
    ap.add_argument("--no-toc", dest="toc", action="store_false", help="不插 @[toc]")
    ap.add_argument("--auto-publish", "--yes", dest="auto_publish", action="store_true", help="跳过确认直接发布")
    ap.add_argument("--dry-run", action="store_true", help="只填元数据，不点最终发布")
    ap.add_argument("--list-columns", action="store_true", help="打开弹窗列出你已有的分类专栏后退出")
    ap.add_argument("--out", help="把结果文章 URL 写入该文件")
    ap.add_argument("--login-wait", type=int, default=120, help="等待登录的最长秒数")
    args = ap.parse_args()

    pw, browser, ctx = connect(args.cdp_url)
    try:
        if args.list_columns:
            page = ctx.new_page()
            list_columns(page)
            return

        if not args.md:
            ap.error("发布模式需要给出 md 文件路径（或用 --list-columns 查看专栏）")
        if not os.path.exists(args.md):
            sys.stderr.write(f"[error] 找不到文件：{args.md}\n"); sys.exit(2)

        with open(args.md, encoding="utf-8") as f:
            raw = f.read()
        fm, body = parse_front_matter(raw)
        body = ensure_toc(body) if args.toc else body

        title = args.title or fm.get("title") or os.path.splitext(os.path.basename(args.md))[0]
        tags = args.tag or (fm.get("tags") if isinstance(fm.get("tags"), list) else None)
        cols = args.column or (fm.get("categories") if isinstance(fm.get("categories"), list) else None)
        summary = args.summary or fm.get("description") or fm.get("summary")
        cover = args.cover or fm.get("image") or fm.get("cover")
        visibility = args.visibility or fm.get("visibility") or "全部可见"

        page = ctx.new_page()
        open_editor_and_login(page, args.login_wait)
        shown_title = load_body_via_import(page, title, body)
        sys.stderr.write(f"[info] 导入后标题显示：{shown_title}\n")

        open_dialog(page)
        if tags:
            add_tags(page, tags)
        if cover:
            set_cover(page, cover)
        if summary:
            set_summary(page, summary)
        if cols:
            select_columns(page, cols)
        set_visibility(page, visibility)

        if args.dry_run:
            sys.stdout.write("[dry-run] 元数据已填，未发布。可在浏览器中核对发布弹窗。\n")
            sys.stdout.write("VERIFY " + json.dumps(verify_dialog(page), ensure_ascii=False) + "\n")
            return

        sys.stdout.write("PRE_PUBLISH_VERIFY " + json.dumps(verify_dialog(page), ensure_ascii=False) + "\n")
        url = publish_and_get_url(page, args.auto_publish)
        if url:
            sys.stdout.write(f"CSDN_URL: {url}\n")
            if args.out:
                with open(args.out, "w", encoding="utf-8") as f:
                    f.write(url + "\n")
    finally:
        pw.stop()  # 只停本地驱动；CDP 连接的用户浏览器保持打开


if __name__ == "__main__":
    main()
