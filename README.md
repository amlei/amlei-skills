# Amlei Skills

A small collection of [Claude Code](https://claude.ai/code) skills. Copy the ones you want into your skills directory.

## Skills

| Skill | Description |
|-------|-------------|
| [amlei-git-gh](skills/amlei-git-gh/SKILL.md) | Git commit, push, and PR workflow using `gh` CLI. Interactive mode with staged/unstaged file review, commit conventions, and PR creation with labels/assignees/reviewers. |
| [amlei-resume-gen](skills/amlei-resume-gen/SKILL.md) | 简历协同创作：和用户一起 0→1 写 / 改局部 / 换岗位重定向 / 迭代简历；个人能力记忆是素材库（KV，脚本管理，写入由独立评估 agent 判断 + 用户确认），简历持久化到项目级。 |
| [amlei-resume-design](skills/amlei-resume-design/SKILL.md) | 把简历 Markdown 装配成 A4 多页 HTML（6 套主题可选），浏览器打开点「导出 PDF」即得 A4 简历；含校验、预览壳、证件照抽取脚本与配色切换。 |
| [amlei-story-generator](skills/amlei-story-generator/SKILL.md) | 故事生成——只需一个主题（书 / 人 / 事 / 物 / 理 / 案），先联网搜索核实，再写成一篇引人入胜的故事长文；钩子开篇、场景先于术语、序号标题、金句定点，独立评判者打分、达标线 90。 |

## Install

Each skill is a standalone directory. Copy it to your skills folder:

```bash
# Personal (all your projects)
cp -r skills/amlei-git-gh ~/.claude/skills/

# Project-only
cp -r skills/amlei-git-gh .claude/skills/
```

Then invoke with `/amlei-git-gh`、`/amlei-resume-gen`、`/amlei-resume-design` 或 `/amlei-story-generator`，或让 Claude 根据上下文自动激活。

## Repository Structure

```
amlei-skills/
├── skills/
│   ├── amlei-git-gh/
│   │   └── SKILL.md
│   ├── amlei-resume-gen/
│   │   ├── SKILL.md
│   │   └── scripts/memory.py          # 个人能力记忆 KV 管理脚本
│   ├── amlei-resume-design/
│   │   ├── SKILL.md
│   │   ├── assets/                    # 预览壳 / 样例简历 / 渲染样例
│   │   ├── references/                # 6 套主题组件库 + 图标库 + 主题索引
│   │   └── scripts/                   # 校验 / 套预览壳 / 证件照抽取
│   └── amlei-story-generator/
│       ├── SKILL.md
│       └── resources/
│           ├── source-frameworks.md   # 六类素材(书/人/事/物/理/案)的拆解骨架
│           ├── narrative-craft.md     # 钩子/标题/场景先于术语 正反例
│           └── rubric.md              # 评判者量化打分标准
└── README.md
```

## License

MIT
