# Amlei Skills

一组 Agent Skills，覆盖简历、求职、写作、Git 工作流等场景。所有 skill 均通过 [`skills-ref`](https://agentskills.io) 校验，符合 [Agent Skills](https://agentskills.io) 开放格式。

## Skills

### 主技能

| Skill | Description |
|-------|-------------|
| [amlei-resume](skills/amlei-resume/SKILL.md) | 简历全流程：就业市场调研 → 项目分析 → 素材挖掘 → 质量评估 → 装配 HTML 导出 A4 PDF + 简历长图；定稿后输出可用于招聘平台的求职招呼语；维护个人能力记忆（profile）跨会话复用 |
| [amlei-story-generator](skills/amlei-story-generator/SKILL.md) | 故事生成——联网核实素材，把任意主题（书 / 人 / 事 / 物 / 理 / 案）写成引人入胜的长文 |
| [amlei-git-gh](skills/amlei-git-gh/SKILL.md) | Git commit / push / PR 工作流（gh CLI），含提交信息规范与 PR 确认门 |
| [amlei-academic-ref-retrieval](skills/amlei-academic-ref-retrieval/SKILL.md) | 学术论文参考文献检索与标准格式输出（知网 / 维普 / arXiv） |

### amlei-resume 的子技能

`amlei-resume` 编排以下 skill 完成各环节，也可独立使用：

| Skill | Description |
|-------|-------------|
| [amlei-job-market-research](skills/amlei-job-market-research/SKILL.md) | 就业市场调研——薪资、能力要求、技术栈、行业趋势与最新动向 |
| [amlei-info-analyze](skills/amlei-info-analyze/SKILL.md) | 信息结构化分析——拆解内容、判断领域，用领域视角提取洞察与结论 |
| [amlei-text-polish](skills/amlei-text-polish/SKILL.md) | 文本润色——逐行分析上下文，在不改原意前提下让文字更清晰有力 |

## Install

```bash
# 作为 Claude Code 插件
claude plugin install npm:amlei-skills

# 或手动复制到标准 skills 目录（项目级 / 用户级二选一）
cp -r skills/amlei-resume      .claude/skills/   # Claude Code
cp -r skills/amlei-resume      .opencode/skills/ # OpenCode
cp -r skills/*                 ~/.agents/skills/ # 跨客户端标准位置
```

## License

MIT
