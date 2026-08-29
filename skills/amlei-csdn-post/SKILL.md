csdn-post skill 更新
---
name: amlei-csdn-post
description: 把本地 Markdown 文件发布成 CSDN 博客文章。复用你【已登录的浏览器】驱动 CSDN 网页编辑器（editor.csdn.net/md/），自动在正文开头插入 @[toc] 目录、归类标签/分类专栏、填写摘要、设置可见范围，并完成发布。自适应你用的任一 Chromium 内核浏览器（Chrome/Edge/Brave/Arc/Vivaldi 等）。当用户要把 md 发到 CSDN、上传博客到 CSDN、CSDN 自动发布、发文章到 CSDN、CSDN 发帖、把笔记/文章同步到 CSDN、csdn post/publish 时使用——哪怕用户没明说"CSDN"，只要意图是"把这篇 md 发到中文技术博客平台"就该用它。
---

# CSDN 发文（md → CSDN 博客）

把一个 `.md` 文件发布成 CSDN 博客文章。核心能力：**正文开头自动加目录**、**自动归类标签/专栏/摘要**、**复用你已登录的浏览器 不重新登录**、**自适应任一 Chromium 内核浏览器**、**发布前默认暂停等你确认**。

## 为什么这样做

CSDN 没有公开稳定的发文 API，后台接口还有加密签名，逆向极易失效。最稳的方式是**直接驱动 CSDN 官方网页编辑器**（`https://editor.csdn.net/md/`），并通过 CDP 连接你"已经登录好账号"的浏览器（任一 Chromium 内核），省去重新登录、绕过验证码。本 skill 内置脚本 `scripts/csdn_publish.py` 做这件事。

> 备选：内部 API + cookie 走无头发布，理论可行但脆弱（接口带加密签名、易被风控），仅作高级选项，本文档不展开。

## 前置条件

1. **浏览器**：任一 Chromium 内核浏览器（Chrome、Edge、Brave、Arc、Vivaldi 等），并在其中**正常登录 CSDN**。脚本会自动探测用的是哪个。
2. **Python 依赖**：`pip install playwright pyperclip`（仓库自带 `.venv`，可用 `.venv/bin/python`；复用已有浏览器，无需 `playwright install`）。
3. **开启浏览器调试（无需拷贝 profile）**：Chrome/Edge 136+ 出于安全禁止在默认 profile 上用 `--remote-debugging-port` 命令行参数，所以不能靠"复制/副本 profile"的老办法。正解是在浏览器里开「远程调试」开关：
   - 打开 `<浏览器>://inspect/#remote-debugging`（如 `edge://inspect`、`chrome://inspect`、`brave://inspect`），勾选 **「Allow remote debugging for this browser instance」**。
   - 脚本会自动探测各浏览器（Chrome/Edge/Brave/Arc/Vivaldi 等）的 `DevToolsActivePort`、读出 WS 端点直连——绕过被屏蔽的 HTTP `/json/version`，复用你现成的 CSDN 登录态，**无需拷贝 profile、无需重登**。
   - 验证：端口在监听即生效（`lsof -iTCP:9222 -sTCP:LISTEN` 能看到浏览器进程）；在该浏览器访问 `https://editor.csdn.net/md/` 不跳登录页即登录态在。
   - 浏览器窗口保持开着即可。脚本不关它、不碰账号密码。注意：**完全重启浏览器后开关会复位，需重新勾选。**

## 输入

1. **Markdown 文件**（必填）：要发布的 `.md` 路径。
2. **元数据来源**（优先级）：命令行参数 > md 的 YAML front matter > 推断。
   - front matter 字段：`title` / `tags`(列表) / `categories`(列表，=分类专栏) / `description`(=摘要) / `image`(封面 URL 或路径) / `toc`(默认 true) / `visibility`。
3. **模式**：默认真实发布；`--dry-run` 只填不发；`--list-columns` 列出你已有的分类专栏。

## 交付

- 成功发布后返回：**文章 URL**（`https://blog.csdn.net/<用户>/article/details/<id>`）+ 实际生效的标题/标签/专栏/摘要/可见范围。
- 默认保留"暂停确认"环节，避免误发。

## 工作流程

### 第 0 步：摸清意图

- 要发布哪个 md？
- 是真发（默认）、还是先 `--dry-run` 试填、还是只想 `--list-columns` 看有哪些专栏？
- 发布是对外、难撤回的动作——**默认要和用户确认元数据后再发**，除非用户明确说"直接发/不用确认"。

### 第 1 步：读 md + 解析 front matter

读文件，解析开头的 YAML front matter（`title`/`tags`/`categories`/`description`/`image`/`toc`/`visibility`）。脚本自带极简解析，不依赖 pyyaml。

### 第 2 步：归类——标签 / 分类专栏 / 摘要

发布要求"归类所属标签、专栏，摘要简介"。front matter 给齐就用 front matter；**缺的由你（执行 LLM）读正文推断，然后跟用户确认**：

| 字段 | 推断要点 | 上限/约束 |
|------|----------|-----------|
| **标签 tags** | 贴合内容的技术关键词，优先 CSDN 高频标签 | 3–5 个，每个 ≤20 字 |
| **分类专栏 categories** | **必须是用户在 CSDN 已创建的专栏名**——先 `--list-columns` 拿真实列表再匹配 | 匹配不到就**跳过并告知**，别瞎填 |
| **摘要 summary** | 一句话说清"这篇解决什么/讲了什么"，吸引点击 | ≤120 字，别照搬第一段 |

> 专栏（分类）在 CSDN 里是用户**预先创建**的容器，不是自由标签。如果你没把握用户有哪些专栏，**先跑 `--list-columns`**，从真实列表里选最贴的；一个都贴不上就空着（专栏是可选的），别硬选。

> **关键流程前提**：标签、分类专栏、摘要、可见范围这些控件**都在点「发布文章」之后弹出的发布弹窗里**，点之前页面上不存在。所以无论是脚本还是人工排查，都必须先把发布弹窗打开，才能定位/点选分类专栏。`--list-columns` 的内部流程就是：打开编辑器 → 点「发布文章」打开弹窗 → 点「新建分类专栏」打开专栏面板 → 列出已有专栏。

### 第 3 步：正文加目录

CSDN 的 Markdown 编辑器支持 `@[toc]` 标记——在正文里单独一行写 `@[toc]`，会**自动根据各级标题生成可点击的目录**。脚本默认把 `@[toc]` 插到正文最前面（已有则不重复）。

- 不想要目录：`--no-toc`，或 front matter 里 `toc: false`。
- 前提：正文里得用 `#`/`##`/`###` 标题，目录才有内容可抽。

### 第 4 步：确认浏览器调试已开启

确认已在你要用的浏览器里勾选「Allow remote debugging for this browser instance」（`<浏览器>://inspect/#remote-debugging`，如 `edge://inspect` / `chrome://inspect` / `brave://inspect`），且已登录 CSDN——见【前置条件 3】。脚本连不上时会提示去开这个开关；**无需拷贝 profile**。

> 开关要用户自己在浏览器里勾（是浏览器的安全放行）。提示用 `! open -a "Microsoft Edge" "edge://inspect/#remote-debugging"`（Chrome 换 `"Google Chrome"` + `chrome://inspect`，Brave 换 `Brave Browser` + `brave://inspect`）在会话里直接打开该页更顺。

### 第 5 步：发布

脚本完整流程：打开编辑器 → 导入 md（文件名即标题）→ 点「发布文章」打开发布弹窗 → 在弹窗内填标签/摘要/分类专栏/可见范围 → 再点弹窗内的「发布文章」按钮正式发布。

```bash
# 用仓库 .venv（也可换系统 python，需已装 playwright + pyperclip）
.venv/bin/python skills/amlei-csdn-post/scripts/csdn_publish.py <文章.md> \
  --tag <标签> --tag <标签> \
  --column "<已有专栏名>" \
  --summary "一句话摘要" \
  [--cover <图>] [--visibility 公开] [--auto-publish]
```

- 不带 `--auto-publish` 时：脚本填完一切后**暂停**，让你在浏览器里核对发布弹窗，回车才点最终发布。
- 想先看填得对不对：加 `--dry-run`。
- 想知道有哪些专栏可选：先跑 `--list-columns`。
- 发布成功，stdout 末行是 `CSDN_URL: <链接>`，解析它返回给用户。

### 第 6 步：核对与交付

拿到 URL 后：打开看一眼目录、标签、专栏、摘要是否都对；把 URL + 生效的元数据告诉用户。

## 规则

1. **复用登录，绝不碰账号密码**：只通过 CDP 连用户已登录的浏览器（任一 Chromium 内核），不要求、不存储、不输入密码或 cookie。
2. **发布前默认确认**：真发布是对外动作，默认 `--auto-publish` 关；除非用户明确授权"直接发"。
3. **专栏只选真实存在的**：从 `--list-columns` 结果里选，匹配不到就空着并说明，绝不编造专栏名。
4. **目录默认开**：正文默认插 `@[toc]`；用户明确不要才关。
5. **不碰用户的浏览器**：脚本全程不 `close()` 连接的浏览器，只在自己结束时停掉本地驱动进程。
6. **不覆盖/不删源 md**：只读取要发布的 `.md`，不修改它。
7. **选择器漂移要会说人话**：CSDN 改版会让选择器失效，报错时引导用户打开 DevTools 重新定位（见排错），而不是反复重试同样的死选择器。

## 常见坑与排错

| 现象 | 原因 / 处理 |
|------|-------------|
| `连不上浏览器 CDP` / `没找到调试端点` | 浏览器的远程调试没开。在 `<浏览器>://inspect/#remote-debugging`（如 `edge://inspect`、`chrome://inspect`、`brave://inspect`）勾选「Allow remote debugging for this browser instance」后重跑；完全重启浏览器后开关会复位，需重新勾选。 |
| 编辑器一直没出现（登录超时） | 该浏览器未登录 CSDN。在窗口里手动登录后重跑；或加大 `--login-wait`。 |
| 正文没灌进去 / 是空的 | 脚本靠编辑器的"导入 Markdown"文件输入（`#import-markdown-file-input`）灌正文；若失败多半是 CSDN 改版换了入口，改脚本对应选择器即可。 |
| `找不到分类专栏「X」` | 专栏名要和 CSDN 后台完全一致；先 `--list-columns` 看真实名称再填。 |
| 定位不到「分类专栏/标签/摘要/可见范围」控件 | 这些控件在点「发布文章」后弹出的发布弹窗里，页面上先只有「发布文章」按钮；先打开弹窗再定位 `.modal__publish-article` 内的控件。`--list-columns` 已封装该流程。 |
| 点「发布文章」后弹窗没出现 | CSDN 改版后按钮可能被覆盖层拦截，普通 click 不生效。 | 改用 force 点击打开弹窗（`page.locator(...).click(force=True)`），脚本 `open_dialog` 已按此修复。 |
| 「添加文章标签」按钮找不到 | 旧选择器依赖父容器 `mark_selection`，CSDN 改版后失效。 | 改为直接定位按钮 `.tag__btn-tag`：`//button[contains(@class,"tag__btn-tag") and contains(normalize-space(.),"添加文章标签")]`，脚本 `SEL["add_tag"]` 已按此修复。 |
| 某个选择器报错（点不动按钮） | CSDN 改版了。F12 开 DevTools，用元素选择器点中目标控件，找个稳定特征（id / placeholder / class 片段），在 Console 用 `$x('xpath')` 或 `$$('css')` 验证能唯一命中，再改 `scripts/csdn_publish.py` 顶部的 `SEL` 字典对应那一项即可——选择器是脚本的唯一事实源。 |
| 发布后没拿到 URL | 看浏览器是否跳转到文章页；脚本会兜底返回当前页 URL，人工核对一下。 |

## 验收自检

发布完成前逐项确认：

- [ ] 正文开头有 `@[toc]` 且 CSDN 渲染出可点击目录（或用户明确要求不加）
- [ ] 标签已归类（3–5 个，贴合内容）
- [ ] 摘要已填（非空，非照搬首段）
- [ ] 分类专栏只勾选了真实存在的（或按用户意愿留空）
- [ ] 可见范围符合用户要求（脚本默认「全部可见」/公开）
- [ ] 拿到并返回了文章 URL
- [ ] 发布前已与用户确认元数据（除非用户授权直发）
