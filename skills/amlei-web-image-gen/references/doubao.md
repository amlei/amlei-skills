# 豆包（doubao.com）图像生成适配器细节

对应实现：`scripts/src/doubao.ts`。豆包前端改版时，按本文件核对 DOM 结构后修改实现。

## 会话模型

- **一次任务 = 一个对话**。进入 `https://www.doubao.com/chat/` 后不再新建对话；
  后续每张图直接在同一条输入框里继续发送。
- 识别「新图」的方法：任务开始前记录会话内所有图片 `<img src>` 基线（`seen` set），
  每次发送后只认基线之外的新增图片。

## 登录态

- 已登录判据：侧栏存在文案匹配 `/^用户/` 的 button（如「用户018069」）。
- 未登录：轮询等待用户在窗口内扫码/手机号登录，默认最长等 180s。
- 登录态来自克隆的 Chrome profile Cookie（解密密钥在 macOS 钥匙串，按应用不按路径，
  因此克隆到临时目录后依然有效）。

## DOM 要点（2026-09 实测）

| 元素 | 定位 |
|------|------|
| 图像生成入口 | `button` 文案「图像生成」（首页工具格） |
| 会话内标志 | composer 工具条出现 `button`「模型」（以此判定是否已在生图会话；不要用「图像生成」文本判定——入口按钮本身也含该文本，会误判） |
| 模型选择 | `button`「模型」→ 菜单项：`Seedream 5.0 Flash`（专业快速，**免费最高档**）/ `Seedream 5.0 Pro`（升级 · 4 倍消耗，付费）/ `Seedream 4.5`（日常生成）/ `Seedream 4.0`（基础生图） |
| 比例选择 | `button`「比例」→ `自动 / 9:16 / 2:3 / 3:4 / 1:1 / 4:3 / 3:2 / 16:9`；**没有 2.35:1** |
| 输入框 | `div.tiptap.ProseMirror[contenteditable=true]`；`keyboard.insert_text` 写入（保留换行），`Enter` 发送 |

## 关键坑

1. **比例菜单必须 Escape 关闭**：选完比例后浮层不自动消失，会拦截输入框的点击（表现为
   `click` 等待时被 `3:2` 等 span intercepts pointer events）。
2. **高清图两段加载**：新图先出现 ~384×215 缩略图，再换成 ~2720×1520 原图。
   等待策略：新图最大宽度 `>=1500` 且连续 2 次轮询（间隔 3s）不变、且页面不忙，才下载。
3. **图片 src 过滤**：只认 `http(s)` 开头（存在 `data:image/svg+xml` 占位）；排除
   `avatar`/`icon`；`naturalWidth >= 200`。
4. **忙碌判定**：`document.body.innerText` 含「生成中 / 正在生成 / 生成图片中」。
5. **下载**：直接 `ctx.request.get(图片src)`（CDN 签名 URL，无需额外 Cookie），
   扩展名按响应 `content-type` 修正（png/jpeg/webp）。

## 浏览器接入

Chrome 进程管理基于本仓 `packages/baoyu-chrome-cdp`（Copy 自 JimLiu/baoyu-skills，MIT），
适配逻辑在 `scripts/src/chrome.ts`：

- 包负责 `findChromeExecutable` / `launchChrome` / `waitForChromeDebugPort`。
- 本仓适配补三件事：① 优雅退出正在运行的日常 Chrome；② 克隆登录态最小文件集
  （`Local State` + `Default/Cookies[-journal]` + `Default/Preferences`，APFS `cp -c`）
  到临时 profile —— 因为 Chrome 136+ 在默认 user-data-dir 上忽略
  `--remote-debugging-port`，而 Cookie 解密密钥在 macOS 钥匙串、与路径无关；
  ③ 启动参数补 `--remote-allow-origins=*`（Chrome 111+ 的 WS Origin 校验，
  缺了它 `/json/version` 通、WebSocket 连不上，表现为 connectOverCDP 30s 超时）。
- **必须 node + tsx 运行**：bun 下 playwright-core 的 WebSocket 连接 CDP 会超时。
- 结束只 `browser.close()`（断 CDP），不杀浏览器进程；用户退出 Chrome 重开即复原。
