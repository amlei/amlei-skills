---
name: resume-design
description: 把简历 Markdown 装配成 A4 多页 HTML（多主题可选），浏览器打开可导出 PDF 打印。触发：简历排版 / 简历转 HTML / 简历导出 PDF / 做 resume / CV。
argument-hint: "[目标岗位或主题] [简历.md 路径]"
---

# resume-design

主题组件库在 `references/theme-{id}.md`，清单见 [theme-index.md](references/theme-index.md)。**装配 HTML 一律从所选主题的组件库取，不凭记忆手写。**

## 工作流

输入是一份「简历 MD 格式」（第 3 步）的 Markdown。

### 1. 选主题

读 [theme-index.md](references/theme-index.md)，据目标岗位 / 行业推荐最契合的主题，让用户一步确认：

- 用户已指定主题 → 直接用。
- 岗位有明确契合 → 推荐 + 1~2 个备选让用户选（岗位 → 主题映射见 theme-index「适用场景」）。
- 无明显倾向 → 默认 `academic`。
- `sidebar-creative` 是双栏单页结构，只能装一页 A4；内容多的简历不要选它。

### 2. 读组件库

读所选主题的 `references/theme-{标识}.md` + 共用的 [icons.md](references/icons.md)（按模块语义选 SVG 图标）。后续装配依据这两份。

### 3. 简历 MD 格式

校验脚本会查的硬规则：

| 元素 | 写法 |
|------|------|
| 首模块 | `# self-intro`（必须是第一个 `#`），下用 `key: value` 放 name / role / gender / location / phone / email / avatar 等 |
| 模块 | `# 模块名`（出现顺序 = 简历模块顺序） |
| 简介 | 模块下纯文本段 |
| 标签 | 模块下「标签, 标签」单行（研究兴趣 / 方向） |
| 经历 | `## 机构 \| 角色/方向`（无 `\|` 则只有机构名） |
| 经历日期 | `date: 2024.07 — 2025.03` |
| 经历补充 | `meta: GPA 3.9/4.0 · 排名 1/60`（关键数字用 `**`） |
| 经历要点 | `- 成就（STAR + 量化）` |
| 技能 | `- 类别: 值` 或 `类别: A · B · C` |

`name:` 必填；`avatar:` 给照片相对路径。完整范例：[sample-resume.md](assets/sample-resume.md)。

### 4. 装配 HTML

按主题库的简历骨架装配：主题 `<style>`（整段照抄）放最前，再依次放各原子——

1. `# self-intro` → **Header** 组件（name/role/contact/photo；不渲染成 SectionHead）。
2. 每个 `# 模块` → **SectionHead**（icon 按 [icons.md](references/icons.md) 选，`data-stick="1"` 必带）+ 模块正文组件（Summary / Interests / Entry / Pubs / Awards / Skills）。
3. `## 机构 | 角色` → **Entry**；其下 `date:` / `meta:` / `- bullets` 收进同一个 Entry。
4. 行内强调：`**词**` → 强调字色；关键数字 / 术语 → 主题的等宽强调（如 `<span class="num">`）。

产物 = `<style>…</style>` + 各原子，**不要**包 `<!DOCTYPE>/<html>/<head>/<body>`（预览壳负责）。

### 5. 校验

用 `scripts/validate_resume.py`（`--help` 看参数；可校验产物 HTML 或简历 MD）。ERROR 清零才算完成（最常见是残留 `{{占位符}}`，详见「易错点」）。

### 6. 套预览壳

用 `scripts/wrap_preview.py`（`--help` 看参数）。

产出 `resume/{姓名}/{求职岗位}/预览.html`（自动建目录，带「导出 PDF」工具条 + A4 自动分页，浏览器打开即可导出）。姓名 / 岗位从产物自动抽取，`document.title` = `姓名-岗位`（=「另存为 PDF」默认文件名）；用 `--name` 覆盖。

### 7. 交付

打开 `resume/{姓名}/{求职岗位}/预览.html` →「导出 PDF」→ 浏览器选「另存为 PDF」即得 A4 简历（工具条打印时自动隐藏），PDF 默认文件名 = `姓名-岗位`。换主题：回第 1 步重选，重新装配 + 校验 + 套壳即可，外壳 / 脚本不变。

参考产物：[sample-preview.html](assets/sample-preview.html)（academic 主题渲染 sample-resume.md 的结果）。

## 头像 / 证件照

证件照用 `scripts/extract_avatar.py`（`--help` 看用法；支持 pdf / docx）从源文件抽取；抽不到（源文件没嵌照片）脚本会报错，让用户提供。抽到后放进产物目录 `resume/{姓名}/{求职岗位}/`，MD 里用 `avatar:` 引用，装配时 Header 用 `<img>`（无照片用 [icons.md](references/icons.md) 占位）。

## 产物目录

所有产物归集到 `resume/{姓名}/{求职岗位}/`（姓名 / 求职岗位两级目录）——相对引用不会断、换岗位 / 换照片互不干扰；换岗位开新的 `{求职岗位}/` 子目录。

## 配色方案

预览页工具条「配色」下拉：8 套点缀色（墨蓝 / 工程蓝 / 森林绿 / 酒红 / 藏青 / 紫 / 琥珀 / 石墨黑）+「主题原色」。选一套，整篇点缀色（标题图标 / 日期 / 强调字 / bullet 符 / 标签底）实时换色；选择记在 localStorage，「导出 PDF」沿用当前配色——同一份简历可出多套配色版本。

切换覆盖的是主题点缀色（不动主题文件；纸张 / 正文 / 版式 / 字号不变），任意主题都能换色。

## A4 与 PDF 导出

- 分页自动：内容超出 A4 自动溢出到下一页，无需手动分页。
- 「导出 PDF」走浏览器原生打印：工具条自动隐藏，输出像素级 A4，离线可用。

## 视觉红线

- **不做报刊排版**：无首字下沉、无报头巨标题、无杂志编号；姓名 ≈24–26px。
- **单点缀色**：一个 `--accent` + 同色系强调字色，不引第二个彩色。
- **默认单栏**；sidebar-creative 用侧栏双栏。
- **可扫描层级**：SectionHead 用发丝线；经历条目 org / role / 日期三段对齐；bullet 用 `•`。
- **量化成就**：经历 bullet 带数字结果，关键数字用强调样式。

## 易错点

- **残留 `{{占位符}}`**：组件模板里的 `{{name}}/{{org}}/{{date}}…` 必须全替换（校验兜底）。
- **`# self-intro` 必须是首个 `#`**，渲染成 Header 而非 SectionHead。
- **`data-stick="1"` 别漏**：SectionHead 必带，否则标题可能独留页底。
- **联系方式按实际字段拼**：没有的字段连同 `<span class="sep">·</span>` 一起删，不留空段。
- **`avatar:` 有就 `<img>`**：照片放进产物同目录；没照片用 icons.md 占位 SVG，别留 `<img src="">`。
- **整篇只用所选主题的组件**，不从别的主题借。
- **标题层级只用 `#`/`##`**：`###`+ 不支持。

## 添加新主题

新主题可直接编写或从参考简历 HTML 转换（规范见 [theme-index.md](references/theme-index.md) 末尾）。写完用 `assets/sample-resume.md` 渲染 → 校验 → 套壳 → 浏览器打开预览核对（即查看主题效果的方式），确认后登记一行到 theme-index。
