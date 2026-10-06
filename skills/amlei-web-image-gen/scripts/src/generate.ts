/**
 * CLI 入口：在同一个平台会话里按顺序生成多张图。
 *
 * 用法：
 *   bun src/generate.ts --job prompt.md=out.png [--job p2.md=out2.png ...] [options]
 *
 * Options:
 *   --platform doubao     平台（目前支持 doubao，默认 doubao）
 *   --model <name>        模型名（默认 Seedream 5.0 Flash，免费最高档）
 *   --ratio <r>           全局比例，如 16:9（无 2.35:1；单张可用 --job p.md=o.png:1:1 覆盖）
 *   --port <n>            CDP 端口（默认 9222）
 *   --timeout <ms>        单张出图超时（默认 300000）
 *   --login-timeout <ms>  登录等待超时（默认 180000）
 *
 * job 简写：--job "prompt.md=out.png" 或 --job "prompt.md=out.png:1:1"（冒号跟比例）。
 */
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";
import { ensureChrome, DEFAULT_PORT } from "./chrome.js";
import { createDoubao } from "./doubao.js";
import type { GenJob, Platform } from "./types.js";

interface Args {
  platform: string;
  model?: string;
  ratio?: string;
  port: number;
  timeout: number;
  loginTimeout: number;
  jobs: GenJob[];
  profileDir?: string;
}

function parseArgs(argv: string[]): Args {
  const args: Args = { platform: "doubao", port: DEFAULT_PORT, timeout: 300_000, loginTimeout: 180_000, jobs: [], profileDir: undefined };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--platform") args.platform = argv[++i];
    else if (a === "--model") args.model = argv[++i];
    else if (a === "--ratio") args.ratio = argv[++i];
    else if (a === "--port") args.port = Number(argv[++i]);
    else if (a === "--profile-dir") args.profileDir = path.resolve(argv[++i]);
    else if (a === "--timeout") args.timeout = Number(argv[++i]);
    else if (a === "--login-timeout") args.loginTimeout = Number(argv[++i]);
    else if (a === "--job") {
      const spec = argv[++i];
      const [pair, ...ratioParts] = spec.split(":");
      const eq = pair.indexOf("=");
      if (eq < 0) throw new Error(`--job 格式应为 prompt.md=out.png[:比例]，收到：${spec}`);
      args.jobs.push({
        promptFile: path.resolve(pair.slice(0, eq)),
        outFile: path.resolve(pair.slice(eq + 1)),
        ratio: ratioParts.length ? ratioParts.join(":") : args.ratio,
      });
    } else throw new Error(`未知参数：${a}`);
  }
  if (args.jobs.length === 0) throw new Error("至少需要一个 --job");
  return args;
}

function loadPlatform(platformId: string, ctx: import("playwright-core").BrowserContext): Platform {
  switch (platformId) {
    case "doubao":
      return createDoubao(ctx);
    default:
      throw new Error(`暂不支持平台：${platformId}（当前支持：doubao）`);
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  let session = await ensureChrome({ port: args.port, profileDir: args.profileDir });
  console.log(`[browser] CDP :${session.port} ${session.reused ? "(附着已有实例)" : "(新启动，克隆 profile)"}`);
  let browser: import("playwright-core").Browser;
  try {
    browser = await chromium.connectOverCDP(`http://127.0.0.1:${session.port}`);
  } catch {
    // 已有实例不带 --remote-allow-origins 时 WS 会被拒：强制重启一次
    session = await ensureChrome({ port: args.port, forceRelaunch: true, profileDir: args.profileDir });
    browser = await chromium.connectOverCDP(`http://127.0.0.1:${session.port}`);
  }
  const { port } = session;
  try {
    const context = browser.contexts()[0] ?? (await browser.newContext());
    const platform = loadPlatform(args.platform, context);
    console.log(`[platform] ${platform.id}`);
    await platform.ensureLogin(args.loginTimeout);
    console.log("[stage] login ok");
    await platform.ensureImageSession(); // 一次任务一个会话，后续 job 全部沿用
    console.log("[stage] image session ok");
    const model = await platform.ensureModel(args.model);
    console.log(`[stage] model ok: ${model}`);
    if (args.ratio) { try { await platform.setRatio(args.ratio); console.log(`[stage] ratio ok: ${args.ratio}`); } catch {} }
    console.log(`[model] ${model}`);
    const seen = new Set<string>(); // 会话内已见图片 URL 基线
    const results = [];
    const failed: string[] = [];
    for (let i = 0; i < args.jobs.length; i++) {
      const job = args.jobs[i];
      if (fs.existsSync(job.outFile) || fs.existsSync(job.outFile + ".jpg") || fs.existsSync(job.outFile + ".webp")) {
        console.log(`[${i + 1}/${args.jobs.length}] SKIP（已存在）${path.basename(job.outFile)}`);
        continue;
      }
      console.log(`[${i + 1}/${args.jobs.length}] ${path.basename(job.outFile)} 生成中…`);
      try {
        const r = await platform.generate(job, seen, args.timeout);
        console.log(`    SAVED ${r.outFile}  ${r.width}x${r.height}  ${(r.bytes / 1024).toFixed(0)}KB`);
        results.push(r);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        console.log(`    FAILED ${job.outFile}: ${msg}`);
        if (msg.includes("QUOTA_EXHAUSTED")) {
          console.log(`今日免费生图额度已用完，停止本批。已完成 ${results.length} 张，剩余任务明天重跑同一命令即可续传（已生成的自动跳过）。`);
          break;
        }
        failed.push(job.outFile);
      }
    }
    if (failed.length) console.log("DONE_WITH_FAILURES\n" + failed.join("\n"));
    else console.log("ALL DONE");
    for (const r of results) console.log(r.outFile);
  } finally {
    await browser.close(); // 只断开 CDP 连接，浏览器进程保留
  }
}

main().catch((e) => {
  console.error("FAILED:", e instanceof Error ? e.message : e);
  process.exit(1);
});
