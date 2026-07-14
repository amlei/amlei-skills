---
name: amlei-resume-gen
description: 简历协同创作：和用户一起 0→1 写 / 改局部 / 换岗位重定向 / 迭代简历；个人能力记忆是素材库（KV，脚本管理，写入由独立评估 agent 判断 + 用户确认）。简历持久化到项目级。触发：写简历 / 生成简历 / 改简历 / 投简历 / resume gen。
argument-hint: "[求职岗位] [意向城市] [工作年限]"
---

# amlei-resume-gen

和用户一起写、改、迭代简历。**个人能力记忆**是素材库（多查、写入谨慎）；**简历**是工作产物（项目级持久化、可反复改）。

## 能力

- **写（0→1）**：从零跟用户一起写目标岗位简历。默认**逐节共创**（个人简介 → 经历 → 技能，每节确认再下一节）；要快可切「先整篇草稿再改」——用户按场景选。
- **改**：改局部 / 换岗位重定向（存成新岗位版本，不覆盖原版）/ 在已存版本上迭代。都直接读写项目级那份简历 MD。
- **记忆联动**：记忆一更新，**主动**告诉用户「要不要把它补进 X 岗位简历」——确认才动。
- **LLM 协同加分**：联网摸岗位画像；**缺口分析**（你有的 vs 岗位要的）；bullet **量化补全**；经历**取舍建议**（相关度低的删/压、亮点前置）；**措辞贴合**岗位关键词。

## 简历存储（项目级，直接读写）

简历是普通 Markdown，持久化在项目级，**不进根目录、不用脚本**——直接 Read / Write：

```
resume/{姓名}/{求职岗位}/简历.md
```

改简历就读这份；换岗就开新的 `{求职岗位}/` 目录存新版（原岗版本保留）。多岗位多版本互不覆盖。

## 写简历（0→1）

1. **聊清目标**：求职岗位、意向城市、工作年限、岗位职责描述（用户粘贴）。
2. **联网调研**：该岗位所需技能 / 候选人画像 / 关键词（中文岗搜中文、英文岗搜英文）。
3. **查记忆**：`memory.py find --tag <岗位方向>` 拉相关能力 / 项目，按岗位相关性取舍。
4. **共创**（默认逐节）：按 个人简介 → 经历 → 技能 顺序，每节基于记忆 + JD 出一版给用户确认 / 改，再下一节。要快就切「先整篇草稿再改」。
5. **落盘**：写到 `resume/{姓名}/{求职岗位}/简历.md`，给用户。
6. 经历用 STAR + 量化，只放与岗位相关的；记忆里的项目地址优先访问核实数据。

## 改简历

- **改局部**：用户指出改哪（段 / bullet / 联系方式）→ 给 before/after → 确认 → 落盘。
- **换岗重定向**：读现岗简历 + 新岗位 → 重排模块、换关键词、从记忆换更贴的项目 → 写到新 `{求职岗位}/` 目录。
- **迭代**：直接在已存版本上按用户要求改。

## 记忆（素材库）

记忆是 KV，由 `scripts/memory.py` 管理，位置优先项目级、否则用户根目录：

- 项目级：`<项目>/.amlei-skill/resume-gen/memory.json`
- 根目录：`~/.amlei-skill/resume-gen/memory.json`

```bash
python3 scripts/memory.py path                              # 记忆在哪 / 是否存在
python3 scripts/memory.py init --location project|root      # 首次创建（不覆盖）
python3 scripts/memory.py time  [--key KEY]                 # 查最后更新时间（判过时）
python3 scripts/memory.py find  [--key KEY] [--tag T] [--category hard|soft] [--type ability|project]
python3 scripts/memory.py add   --type ability|project --key KEY --value "..." [--category] [--tags a,b] [--long-term] [--url URL] [--tech a,b] [--role R] [--outcome O]
python3 scripts/memory.py update --type ability|project --key KEY --field <字段> --value "..."
```

**写简历前必须先有记忆**——`path` 查不到就问用户选项目级 / 根目录，`init` 创建后再引导补充；没有记忆硬性不往下走。

### 写入记忆：独立评估 agent + 用户确认

用户每次补充个人信息，**写入前先派一个独立评估 agent 判断「值不值得记」**（独立上下文、避免自评偏袒），再由用户确认才写：

- 工具：**Agent**（subagent_type: `general-purpose`）。
- 传给它：用户的新描述 + 相关已有记忆（先 `memory.py find`）+ 目标岗位方向。
- 它按四条评估：①硬 / 软实力（硬优先）②长期价值（跨岗位有用才记）③岗位核心方向（核心才记并打标签）④是否过时（与已有冲突 / 陈旧 → 建议更新而非新增）。
- 它输出：是否值得记 + 记成什么（ability / project、key、category、tags、long_term）+ 理由。
- **评估通过且用户确认后**，才调 `memory.py add` / `update`；不通过就告诉用户为什么不记。

> 脚本写入前会自动备份 `memory.json.bak`；但记忆不可撤回，仍以「评估 agent + 用户确认」双保险为准。

## 简历格式

```
# self-intro
name: …                         # 必填
role: 意向岗位 · …
gender: / location: / phone: / email: / avatar:   # 有哪个写哪个

# 个人简介
（一段；关键短语用 ** 标）

# 教育背景 / 实习经历 / 项目经历 / 技能 / …      # 模块按岗位重要性排；# 出现顺序 = 简历顺序
## 机构 | 角色/方向                              # 经历条目（| 分割机构与角色）
date: 2024.07 — 2025.03
meta: GPA 3.9/4.0 · 排名 1/60
- 成就（STAR + 量化）                            # bullet
- 类别: 值                                       # 技能行
```

## 源文档 → 简历素材

用户给 `.docx` / `.pdf` 旧简历：`pandoc` / 抽文本 → 重排成上面格式当素材；要写入记忆走「评估 + 确认」。
