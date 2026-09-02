# Amlei Skills

![Agent Skills](https://img.shields.io/badge/format-Agent_Skills-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Compatible](https://img.shields.io/badge/compatible-Claude_Code_|_OpenCode_|_Agents-black)

一组开箱即用的 Agent Skills，覆盖内容创作、研究分析、视觉设计与 Git 工作流等场景。所有 skill 均通过 [`skills-ref`](https://agentskills.io) 校验，符合 [Agent Skills](https://agentskills.io) 开放格式。

> A collection of production-ready Agent Skills: theme illustration & software logo prompt design, story generation, podcast outlines, industry research, CSDN publishing and Git workflow — compatible with Claude Code, OpenCode and any Agent Skills-compatible client.

## Highlights

- **提示词设计方法论**：全正向描述、设计四律（中心主体 / 白底 / 颜色在主体 / 自成一体）、一形多读
- **中文场景原生**：九宫格、CSDN、知网 / 维普等中文互联网母语符号与信源
- **真实数据优先**：文献检索与产业研究均强制访问一手来源，拒绝编造

## Skills

### 内容创作

| Skill | Description |
|-------|-------------|
| [amlei-story-generator](skills/amlei-story-generator/SKILL.md) | 故事生成——联网核实素材，把任意主题（书 / 人 / 事 / 物 / 理 / 案）写成引人入胜的长文 |
| [amlei-podcast-outline](skills/amlei-podcast-outline/SKILL.md) | 播客大纲制作——把书 / 灵感想法 / 嘉宾对谈变成可直接照着录制的分段口播大纲 |
| [amlei-csdn-post](skills/amlei-csdn-post/SKILL.md) | CSDN 发布——复用已登录浏览器，把本地 Markdown 一键发布成 CSDN 博客文章（自动目录 / 标签 / 摘要 / 可见范围） |

### 研究分析

| Skill | Description |
|-------|-------------|
| [amlei-industry-master](skills/amlei-industry-master/SKILL.md) | 宏观产业研究——「信号触发 · 定向深挖」全闭环：从新闻 / 财报出发双轴扫描产业链，强制原文引用与双语对照，产出深度调研 |
| [amlei-info-analyze](skills/amlei-info-analyze/SKILL.md) | 信息结构化分析——拆解内容、判断领域，用领域视角提取关键洞察与结论 |
| [amlei-academic-ref-retrieval](skills/amlei-academic-ref-retrieval/SKILL.md) | 学术参考文献检索——从知网 / 维普 / arXiv 等权威源提取真实文献，按标准格式输出 |

### 设计与视觉

| Skill | Description |
|-------|-------------|
| [amlei-theme-illustrator](skills/amlei-theme-illustrator/SKILL.md) | 主题插画提示词设计——从内容主题转译为场景瞬间，产出卡通 3D 风格、全正向描述的插画提示词（播客单集封面 / 文章配图 / 内容营销图）；封面设计灵感借鉴 [知行小酒馆](https://www.xiaoyuzhoufm.com/podcast/6013f9f58e2f7ee375cf4216) 播客的节目封面 |
| [amlei-symbolist](skills/amlei-symbolist/SKILL.md) | 软件 Logo 提示词设计——从产品核心行为推演图形概念（行为转译 / 文化母语符号 / 数量精确对应 / 一形多读），遵循设计四律：中心主体、白底、颜色在主体、自成一体 |
| [amlei-md2img](skills/amlei-md2img/SKILL.md) | Markdown 转图片长图——pandoc + Playwright 按移动端宽度整页截图，保留标题 / 代码块 / 列表样式 |

### 开发工作流

| Skill | Description |
|-------|-------------|
| [amlei-git-gh](skills/amlei-git-gh/SKILL.md) | Git commit / push / PR 工作流（gh CLI），含提交信息规范与 PR 确认门 |

## Install

```bash
# 作为 Claude Code 插件
claude plugin install npm:amlei-skills

# 或手动复制到标准 skills 目录（项目级 / 用户级二选一）
cp -r skills/amlei-theme-illustrator .claude/skills/   # Claude Code
cp -r skills/amlei-theme-illustrator .opencode/skills/ # OpenCode
cp -r skills/*                        ~/.agents/skills/ # 跨客户端标准位置
```

## License

MIT
