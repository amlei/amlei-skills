# Amlei Skills

A small collection of [Claude Code](https://claude.ai/code) skills. Copy the ones you want into your skills directory.

## Skills

| Skill | Description |
|-------|-------------|
| [git-gh](skills/git-gh/SKILL.md) | Git commit, push, and PR workflow using `gh` CLI. Interactive mode with staged/unstaged file review, commit conventions, and PR creation with labels/assignees/reviewers. |
| [skill-creation](skills/skill-creation/SKILL.md) | Guide for creating Claude Code skills following the official Agent Skills standard. Covers frontmatter, invocation control, paths filtering, dynamic context, and subagent execution. |

## Install

Each skill is a standalone directory. Copy it to your skills folder:

```bash
# Personal (all your projects)
cp -r skills/git-gh ~/.claude/skills/

# Project-only
cp -r skills/git-gh .claude/skills/
```

Then invoke with `/git-gh` or `/skill-creation`, or let Claude auto-activate based on context.

## Repository Structure

```
amlei-skills/
├── skills/
│   ├── git-gh/SKILL.md
│   └── skill-creation/
│       ├── SKILL.md
│       └── resources/
└── README.md
```

## License

MIT
