---
name: amlei-web-image-gen
description: 通过浏览器自动化调用网页版 AI 生图（平台：豆包 doubao.com，目前仅支持豆包，默认豆包）。复用用户 Chrome profile 的登录态（克隆 profile 绕过 Chrome 136+ 的默认目录调试限制），在同一个会话中按提示词文件逐张生成并下载原图。触发场景：用户提到「用豆包生图」「doubao 生图」「网页版 AI 生图」「把提示词拿到豆包生成」「web image gen」时使用。
---

# web-image-gen

用浏览器自动化在网页版 AI 生图平台（豆包）批量生成图片。**一次任务中的所有图片只在同一个对话（会话）里连续生成**。

## 前置依赖

- macOS + Google Chrome（用户日常 profile 中已登录目标平台）
- Node.js + tsx：`scripts/` 下首次使用先 `npm install`（依赖仅 `playwright-core`，不下载浏览器，附着系统 Chrome）
- ⚠️ 必须用 **node + tsx** 运行，不要用 bun（bun 下 playwright WebSocket 连不上 CDP）

## 输入

1. **提示词文件**（一个或多个）：baoyu 风格 `.md`（含 YAML frontmatter 亦可，发送前自动剥离 frontmatter）。
2. **输出路径**：每张图的目标 `.png` 路径。
3. **平台**：`--platform doubao`（默认，目前唯一支持）。
4. **模型**：默认 `Seedream 5.0 Flash`（免费最高档；`5.0 Pro` 需订阅且 4 倍消耗，不要擅自选）。
5. **比例**：豆包支持 `自动/9:16/2:3/3:4/1:1/4:3/3:2/16:9`，**没有 2.35:1**；默认 `16:9`。

## 命令

```sh
cd skills/amlei-web-image-gen/scripts
npm install
npx tsx src/generate.ts \
  --platform doubao \
  --job "prompts/01-cover.md=out/cover.png" \
  --job "prompts/02-scene.md=out/02-scene.png:16:9" \
  --ratio 16:9 --model "Seedream 5.0 Flash"
```

`--job` 可重复；格式 `提示词.md=输出.png[:比例]`。其它参数：`--port 9222`、`--timeout 300000`（单张出图超时）、`--login-timeout 180000`。

## 工作流程

1. 确认提示词文件存在；确认输出目录可写。
2. 运行命令（脚本自动完成浏览器接入，见下）。**一次任务的所有 `--job` 放进同一条命令**——它们会在同一个豆包对话里连续生成。
3. 首次运行若未登录，脚本会轮询等待，此时提示用户在弹出的 Chrome 窗口里扫码/登录。
4. 逐张下载完成后脚本打印 `SAVED` 行与最终文件清单；把**文件路径 + 实际分辨率**汇报给用户。
5. 单张失败（超时/无新图）时：可重跑该张（新开一条只含该 `--job` 的命令，会沿用同一浏览器实例）。

## 浏览器接入（脚本自动处理，用户无需关心）

Chrome 进程管理基于本仓 `packages/baoyu-chrome-cdp`（Copy 自 JimLiu/baoyu-skills，MIT），
适配逻辑在 `scripts/src/chrome.ts`：

- Chrome 136+ 在**默认 user-data-dir** 上忽略 `--remote-debugging-port`。脚本会把登录态最小文件集（`Local State`、`Default/Cookies[-journal]`、`Default/Preferences`）用 APFS `cp -c` 克隆到临时 profile，再以该目录启动带 CDP 的 Chrome（含 `--remote-allow-origins=*`）。
- Cookie 解密密钥在 macOS 钥匙串（按应用不按路径），克隆后的登录态有效。
- 已有 CDP 实例则直接附着；附着失败（旧实例缺 allow-origins）自动强制重启一次。
- 结束时脚本只断开 CDP 连接、**不关浏览器**；任务全部结束后用户可直接退出 Chrome 再正常打开即可复原。

## 平台细节

豆包适配器的 DOM 选择器、模型清单、忙碌判定、高清图等待策略等细节见 [references/doubao.md](references/doubao.md)。豆包页面改版导致失败时，先核对该文件的「DOM 要点」一节再改 `scripts/src/doubao.ts`。

## 额度限制（自动处理）

豆包免费生图有每日次数限制。脚本在发送与等待轮询中检测页面文案
（「次数用完」「开通豆包专业版…创作额度」「创作额度不足」），命中即抛
`QUOTA_EXHAUSTED` 并**立即停止本批**（不再逐张空转），已完成的图保留。
第二天重跑同一条命令即可续传（已存在的 png 自动跳过）。若要当天继续，
需在豆包页面开通专业版或购买创作额度包后重跑。

## 约束与注意事项

- 生图在用户自己的登录账号下进行，消耗的是账号免费额度；不要并发、不要超量，逐张顺序生成。
- 模型默认且默认即免费最高档；不要主动选择带「升级」标记的模型。
- 提示词文件里若声明 2.35:1 等豆包不支持的比例，以 `--ratio` 实际传值为准（封面可出 16:9，或靠提示词让模型贴近 2.35:1，如本次 3008×1280）。
- 生成内容遵守平台规则；提示词包含真人、敏感主题时先与用户确认。
