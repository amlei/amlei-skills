/**
 * 豆包（doubao.com）图像生成适配器。
 *
 * 会话模型：一次任务里的所有出图都发生在同一个对话里——
 * 进入 chat 页后不再新建对话，逐条发送提示词，靠「已见图片 URL 基线」识别每次的新图。
 *
 * DOM 要点（2026-09 实测，DOM 变了先改这里）：
 * - 登录态：侧栏有文案为「用户*」的 button；未登录会出现登录引导。
 * - 图像生成入口：button「图像生成」；激活后输入框上方出现「图像生成 ×」chip，且在同一对话内持续生效。
 * - 模型：button「模型」→ 菜单项 Seedream 5.0 Flash（专业快速，免费最高档）/ 5.0 Pro（升级·4 倍消耗）/ 4.5 / 4.0。
 * - 比例：button「比例」→ 自动/9:16/2:3/3:4/1:1/4:3/3:2/16:9（无 2.35:1）。
 *   选择后必须按 Escape 关闭菜单，否则浮层会挡住输入框的点击。
 * - 输入框：div.tiptap.ProseMirror[contenteditable=true]，用 keyboard.insert_text 写入（保换行），Enter 发送。
 * - 结果图：<img>，真实图为 http(s) 的 byteimg CDN 地址；
 *   过滤 src 以 http 开头、排除 avatar/icon、naturalWidth>=200。
 *   新图先加载 384x215 缩略图，再换成 2720x1520 原图——必须等宽度稳定（>=1500 且连续两次轮询不变）再下载。
 * - 忙碌判定：body 文本包含「生成中/正在生成」。
 */
import fs from "node:fs";
import path from "node:path";
import type { BrowserContext, Page } from "playwright-core";
import type { GenJob, GenResult, Platform } from "./types.js";

const CHAT_URL = "https://www.doubao.com/chat/";
const FREE_MODEL = "Seedream 5.0 Flash";

function stripFrontmatter(text: string): string {
  if (text.startsWith("---")) {
    const end = text.indexOf("\n---", 3);
    if (end > 0) return text.slice(text.indexOf("\n", end + 1)).trim();
  }
  return text.trim();
}

async function chatImages(page: Page): Promise<Array<{ src: string; w: number; h: number }>> {
  return page.evaluate(() => {
    const out: Array<{ src: string; w: number; h: number }> = [];
    document.querySelectorAll("img").forEach((im) => {
      const src = (im as HTMLImageElement).currentSrc || im.getAttribute("src") || "";
      if (!src.startsWith("http")) return;
      if (src.includes("avatar") || src.includes("icon")) return;
      const r = im.getBoundingClientRect();
      if ((im as HTMLImageElement).naturalWidth >= 200 && r.width > 60)
        out.push({ src, w: (im as HTMLImageElement).naturalWidth, h: (im as HTMLImageElement).naturalHeight });
    });
    return out;
  });
}

async function isBusy(page: Page): Promise<boolean> {
  const text = await page.evaluate(() => document.body.innerText).catch(() => "");
  return text.includes("生成中") || text.includes("正在生成") || text.includes("生成图片中");
}

export function createDoubao(ctx: BrowserContext): Platform {
  const page: Page = ctx.pages().find((p) => p.url().includes("doubao.com")) ?? ctx.pages()[0];

  const platform: Platform = {
    id: "doubao",

    async ensureLogin(timeoutMs = 180_000) {
      await page.bringToFront();
      if (!page.url().includes("doubao.com")) await page.goto(CHAT_URL, { waitUntil: "domcontentloaded" });
      await page.waitForTimeout(3000);
      const deadline = Date.now() + timeoutMs;
      while (Date.now() < deadline) {
        const loggedIn = await page
          .getByRole("button", { name: /^用户/ })
          .first()
          .isVisible()
          .catch(() => false);
        if (loggedIn) return;
        console.log("[doubao] 未检测到登录态，请在打开的窗口中登录（扫码/手机号）…");
        await page.waitForTimeout(10_000);
      }
      throw new Error("doubao 登录等待超时");
    },

    async ensureImageSession() {
      await page.bringToFront();
      // 判定是否已在图像生成会话：composer 工具条出现「模型」按钮
      const inSession = async () =>
        page.getByRole("button", { name: "模型" }).first().isVisible().catch(() => false);
      if (await inSession()) return;
      const activate = async () => {
        await page.goto(CHAT_URL, { waitUntil: "domcontentloaded" });
        await page.waitForTimeout(3000);
        await page.getByRole("button", { name: "图像生成" }).first().click();
        await page.waitForTimeout(2500);
      };
      await activate();
      for (let i = 0; i < 3 && !(await inSession()); i++) {
        await page.waitForTimeout(3000);
        if (i === 1) await activate();
      }
      if (!(await inSession())) throw new Error("未能进入图像生成会话（找不到「模型」按钮）");
    },

    async setRatio(ratio: string) {
      const ratioBtn = page.getByRole("button", { name: "比例" }).first();
      await ratioBtn.waitFor({ state: "visible", timeout: 15_000 });
      const label = await ratioBtn.innerText();
      if (label.replace(/\s+/g, " ").includes(ratio)) return;
      await ratioBtn.click();
      await page.waitForTimeout(1200);
      await page.getByRole("button", { name: ratio, exact: true }).first().click();
      await page.waitForTimeout(600);
      await page.keyboard.press("Escape"); // 必须关菜单，否则浮层挡住输入框
      await page.waitForTimeout(800);
    },

    async ensureModel(model?: string) {
      const want = model ?? FREE_MODEL;
      const modelBtn = page.getByRole("button", { name: "模型" }).first();
      await modelBtn.waitFor({ state: "visible", timeout: 15_000 });
      const label = await modelBtn.innerText();
      if (label.replace(/\s+/g, " ").includes(want)) return want;
      await page.getByRole("button", { name: "模型" }).first().click();
      await page.waitForTimeout(1500);
      await page.getByText(want, { exact: false }).first().click();
      await page.waitForTimeout(1000);
      await page.keyboard.press("Escape");
      await page.waitForTimeout(500);
      return want;
    },

    async generate(job: GenJob, seen: Set<string>, timeoutMs = 300_000): Promise<GenResult> {
      if (job.ratio) await platform.setRatio(job.ratio);
      const prompt = stripFrontmatter(fs.readFileSync(job.promptFile, "utf8"));

      const composer = page.locator("div.tiptap.ProseMirror[contenteditable=true]").first();
      await composer.click();
      await page.waitForTimeout(400);
      await page.keyboard.insertText(prompt);
      await page.waitForTimeout(600);
      await page.keyboard.press("Enter");
      await page.waitForTimeout(4000);

      const deadline = Date.now() + timeoutMs;
      let news: Array<{ src: string; w: number; h: number }> = [];
      let hiStable = 0;
      let lastW = 0;
      while (Date.now() < deadline) {
        news = (await chatImages(page)).filter((i) => !seen.has(i.src));
        if (news.length > 0) {
          const w = Math.max(...news.map((i) => i.w));
          if (w >= 1500 && w === lastW) {
            hiStable++;
            if (hiStable >= 2 && !(await isBusy(page))) break;
          } else {
            hiStable = 0;
          }
          lastW = w;
        }
        await page.waitForTimeout(3000);
      }
      if (news.length === 0)
        throw new Error(`出图超时（${timeoutMs}ms）：${job.outFile}。可重试或检查会话页。`);
      for (const n of news) seen.add(n.src);
      const best = news.reduce((a, b) => (a.w * a.h >= b.w * b.h ? a : b));
      const resp = await ctx.request.get(best.src, { timeout: 60_000 });
      const buf = await resp.body();
      const ct = resp.headers()["content-type"] ?? "";
      const ext = ct.includes("jpeg") || ct.includes("jpg") ? ".jpg" : ct.includes("webp") ? ".webp" : ".png";
      const finalPath = job.outFile.endsWith(ext) ? job.outFile : job.outFile + ext;
      fs.mkdirSync(path.dirname(finalPath), { recursive: true });
      fs.writeFileSync(finalPath, buf);
      return { outFile: finalPath, width: best.w, height: best.h, bytes: buf.byteLength };
    },
  };
  return platform;
}
