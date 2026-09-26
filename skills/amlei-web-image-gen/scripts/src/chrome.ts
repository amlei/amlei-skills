/**
 * Chrome 接入层 —— 基于 baoyu-chrome-cdp 包的薄适配。
 *
 * 包提供通用的 findChromeExecutable / launchChrome / waitForChromeDebugPort；
 * 本文件只补三件平台相关的事：
 * 1. 优雅退出正在运行的 Chrome（用户日常实例会占住登录 profile）；
 * 2. 克隆登录态最小文件集到临时 profile（Chrome 136+ 在默认 user-data-dir 上
 *    忽略 --remote-debugging-port，Cookie 解密密钥在 macOS 钥匙串、与路径无关，
 *    因此克隆后登录态依然有效）；
 * 3. 启动参数补上 --remote-allow-origins=*（Chrome 111+ 的 WS Origin 校验，
 *    缺了它 /json/version 通但 WebSocket 连不上）。
 */
import { execFileSync, spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  findChromeExecutable,
  launchChrome,
  waitForChromeDebugPort,
} from "baoyu-chrome-cdp";

export const DEFAULT_PORT = 9222;

const CHROME_CANDIDATES = {
  darwin: ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
  win32: [],
  default: ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable"],
};

const PROFILE_SRC = path.join(os.homedir(), "Library", "Application Support", "Google", "Chrome");

export interface EnsureChromeResult {
  port: number;
  profileDir: string;
  reused: boolean;
  chrome?: ReturnType<typeof launchChrome>;
}

async function cdpAlive(port: number): Promise<boolean> {
  try {
    const res = await fetch(`http://127.0.0.1:${port}/json/version`, { signal: AbortSignal.timeout(3000) });
    return res.ok && JSON.stringify(await res.json()).includes("Browser");
  } catch {
    return false;
  }
}

function running(): boolean {
  try {
    return execFileSync("pgrep", ["-x", "Google Chrome"], { encoding: "utf8" }).trim().length > 0;
  } catch {
    return false;
  }
}

export function quitChrome(force = false, matchDir?: string): void {
  try {
    if (matchDir) {
    // 只退使用指定 profile 的实例，不动用户其它 Chrome 窗口
    try { execFileSync("pkill", ["-f", matchDir], { timeout: 5000 }); } catch {}
    return;
  }
  try { execFileSync("osascript", ["-e", 'quit app "Google Chrome"'], { timeout: 10_000 }); } catch {}
  } catch {
    /* 未在运行 */
  }
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 2000);
  if (force && running()) {
    try {
      execFileSync("pkill", ["-x", "Google Chrome"], { timeout: 5000 });
    } catch {
      /* ignore */
    }
  }
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 1000);
}

/** 克隆登录态最小文件集（APFS clone，瞬时完成）。 */
export function cloneProfile(src: string = PROFILE_SRC, dst?: string): string {
  const target = dst ?? fs.mkdtempSync(path.join(os.tmpdir(), "web-image-gen-chrome-"));
  fs.mkdirSync(path.join(target, "Default"), { recursive: true });
  for (const rel of ["Local State", "Default/Cookies", "Default/Cookies-journal", "Default/Preferences"]) {
    const from = path.join(src, rel);
    if (!fs.existsSync(from)) continue;
    const to = path.join(target, rel);
    try {
      execFileSync("cp", ["-c", from, to]);
    } catch {
      fs.copyFileSync(from, to);
    }
  }
  return target;
}

export async function ensureChrome(opts: { port?: number; forceRelaunch?: boolean; profileDir?: string } = {}): Promise<EnsureChromeResult> {
  const port = opts.port ?? DEFAULT_PORT;
  if (cdpAliveSync(port) && !opts.forceRelaunch) return { port, profileDir: opts.profileDir ?? "", reused: true };

  if (opts.forceRelaunch) quitChrome(true);
  const profileDir = opts.profileDir && fs.existsSync(opts.profileDir) ? opts.profileDir : cloneProfile();
  const chromePath = findChromeExecutable({ candidates: CHROME_CANDIDATES, envNames: ["CHROME_PATH"] });
  if (!chromePath) throw new Error("未找到 Chrome 可执行文件");
  const chrome = launchChrome({
    chromePath,
    profileDir,
    port,
    extraArgs: [
      "--profile-directory=Default",
      "--remote-allow-origins=*",
      "--window-size=1440,900",
    ],
  });
  // launchChrome 用 spawn 返回 ChildProcess，这里 detachment 由包内部 stdio:"ignore" 完成；
  // 进程句柄不持有引用即可常驻。
  void chrome;
  await waitForChromeDebugPort(port, 30_000);
  return { port, profileDir, reused: false, chrome };
}

function cdpAliveSync(port: number): boolean {
  try {
    const out = execFileSync("curl", ["-s", "--max-time", "3", `http://127.0.0.1:${port}/json/version`], {
      encoding: "utf8",
    });
    return out.includes("Browser");
  } catch {
    return false;
  }
}
