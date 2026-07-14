# Amlei Skills

A small collection of [Claude Code](https://claude.ai/code) skills. Copy the ones you want into your skills directory.

## Skills

| Skill | Description |
|-------|-------------|
| [amlei-git-gh](skills/amlei-git-gh/SKILL.md) | Git commit, push, and PR workflow using `gh` CLI. Interactive mode with staged/unstaged file review, commit conventions, and PR creation with labels/assignees/reviewers. |
| [amlei-story-generator](skills/amlei-story-generator/SKILL.md) | 故事生成——只需一个主题（书 / 人 / 事 / 物 / 理 / 案），先联网搜索核实，再写成一篇引人入胜的故事长文；钩子开篇、场景先于术语、序号标题、金句定点，独立评判者打分、达标线 90。 |

## Install

Each skill is a standalone directory. Copy it to your skills folder:

```bash
# Personal (all your projects)
cp -r skills/amlei-git-gh ~/.claude/skills/

# Project-only
cp -r skills/amlei-git-gh .claude/skills/
```

Then invoke with `/amlei-git-gh` or `/amlei-story-generator`, or let Claude auto-activate based on context.

## Repository Structure

```
amlei-skills/
├── skills/
│   ├── amlei-story-generator/
│   │   ├── SKILL.md
│   │   └── resources/
│   │       ├── source-frameworks.md  # 六类素材(书/人/事/物/理/案)的拆解骨架
│   │       ├── narrative-craft.md    # 钩子/标题/场景先于术语 正反例
│   │       └── rubric.md             # 评判者量化打分标准
│   └── amlei-git-gh/SKILL.md
└── README.md
```

## License

MIT
