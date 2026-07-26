---
name: amlei-md2img
description: 把 Markdown 文件渲染成图片长图（PNG）。用 pandoc 转 HTML，再通过 Playwright 按移动端宽度整页截图，保留标题、代码块、列表等样式。当用户需要把 md 转成图片、生成文章分享长图、markdown to image、md 截图、把文档导出为图片时使用。
---

# md2img

把 Markdown 渲染成一张 PNG 长图：`pandoc`(gfm→html5) → 套用 `references/themes/` 中的 HTML 主题模板 → Playwright 整页截图。默认按 390px 移动端宽度、3 倍设备缩放渲染，适合微信/社交分享。

## 前置依赖

- **pandoc**（系统命令）：`brew install pandoc`
- **Playwright**（Python 包）+ 浏览器：`pip install playwright && playwright install chromium`
- 缺浏览器时可改用本机已装的 Edge/Chrome：脚本传 `--channel msedge`（或 `chrome`）

## 输入

1. **Markdown 文件**：要渲染的 `.md` 文件路径。
2. **输出路径**（可选）：目标 PNG 路径，默认与输入同名换 `.png` 后缀。
3. **主题**（可选）：`references/themes/` 下的主题名（默认 `default`）。
4. **渲染参数**（可选）：宽度（默认 390）、缩放倍数（默认 3）、浏览器 channel（默认 Playwright 自带 chromium）。

## 交付

渲染好的 PNG 文件（默认同时保留中间 HTML 便于调试，可用 `--no-html` 删除）。返回：**PNG 文件路径** + 字节数。

## 工作流程

1. 确认输入 `.md` 文件存在；不存在则停下并提示用户。
2. 确认依赖：`pandoc --version` 与 Playwright 浏览器是否就绪；缺失则给出安装命令，不擅自安装。
3. 确认输出参数（路径 / 主题 / 宽度 / 缩放）；用户未指定则用默认值。
4. 运行脚本：`python skills/amlei-md2img/scripts/md2img.py <input.md> [-o out.png] [--theme default] [--width N] [--scale N] [--channel msedge]`。
5. 渲染完成后返回 PNG 路径；若图片异常（空白/截断），检查中间 HTML 并排查（网络图片未加载、CSS 失效等）。

## 主题模板

主题放在 `references/themes/<name>.html`，是完整的 HTML 文档，必须包含 `{{body}}` 占位符（pandoc 输出注入处），可选 `{{title}}`（替换为输入文件名）。脚本按 `--theme <name>` 解析为 `references/themes/<name>.html`；也可直接传一个 `.html` 文件路径。内置 5 套主题：

| name | 风格 | 明暗 | 特征 |
|------|------|------|------|
| `default` | blueprint 蓝图技术风 | 浅 | 方格底板 + 纸质卡片 + 琥珀强调 + `S/01` 章节标 |
| `dusk` | 深色编辑风 | 深 | 渐变标题（青→蓝→紫）+ 渐变章节边 |
| `riso` | 孔版印刷/risograph | 浅 | 半色调底纹 + 粉色错印投影 + 粗体大写 |
| `ink` | 宣纸水墨 + 朱砂印章 | 浅 | 红印章 + 首字下沉 + 宋体衬线 |
| `magazine` | 杂志色块封面 | 浅 | 通栏森林绿标题色块 + 金色点缀 |

设计原则：**克制装饰，突出正文**——线条用细线（1–2px）、表头用浅色描边而非实心色块，每套只保留一个招牌特征。

新增主题只需往该目录放一个带 `{{body}}` 的 `.html` 文件，无需改脚本。

## 类型化引用块（callouts）

支持 GitHub 风格提示，pandoc 会把 `> [!TYPE]` 转成带图标的彩色块（信息 / 灯泡 / 铃铛 / 警告 / 停止），普通 `>` 仍是普通引用：

```
> [!NOTE]
> 补充背景信息。

> [!TIP]
> 给个小技巧。

> [!IMPORTANT]    > [!WARNING]    > [!CAUTION]
> 务必注意。       > 操作有风险。   > 可能不可逆。
```

| 类型 | 含义 | 图标 |
|------|------|------|
| `[!NOTE]` | 备注 | info 圆 |
| `[!TIP]` | 建议 | 灯泡 |
| `[!IMPORTANT]` | 重要 | 铃铛 |
| `[!WARNING]` | 警告 | 三角 |
| `[!CAUTION]` | 谨慎 | 八角 |

图标与配色由 `references/themes/_callouts.css`（浅色）与 `_callouts-dark.css`（深色 / dusk）定义，主题通过 `{{callouts}}` / `{{callouts-dark}}` 占位符在渲染时**内联**进 HTML（产物自包含，不依赖外部文件）。改图标/配色只需改这两个文件。

## 规则

1. **不改源文件**：只读取输入 `.md`，不修改其内容。
2. **不覆盖已有输出**：目标 PNG 已存在时先与用户确认，或改写到新文件名，不静默覆盖。
3. **中间产物显式可控**：默认保留 `.html` 中间文件便于排查，提供 `--no-html` 在确认无需时清理。
4. **依赖缺失先提示**：pandoc 或 Playwright 未就绪时给出对应安装命令，不替用户执行系统级安装。
5. **路径以 cwd 为准**：脚本在当前工作目录下读写相对路径，调用前确认 cwd 正确。

## 验收自检

交付前逐项确认，任何一项不通过则补齐后再交付：

- [ ] 输入 `.md` 文件存在且可读
- [ ] pandoc 与 Playwright 浏览器均就绪
- [ ] 输出 PNG 已生成且非空（字节数 > 0）
- [ ] 未覆盖任何已有文件（或已征得确认）
- [ ] 返回内容只有 PNG 路径 + 字节数，不含冗余正文
