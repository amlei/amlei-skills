# AGENTS.md

npm-published Claude Code plugin — **reusable utility skills only**（不放完整工作流 skill）。No build/test/lint (doc-only repo).

> 简历全流程 skill（`amlei-resume` + `amlei-profile`）已拆到独立仓库 [amlei/amlei-resume](https://github.com/amlei/amlei-resume)。本仓只保留可复用 utility skill。

## Owned skills (`skills/`)

| Skill | Path | 用途 |
|-------|------|------|
| amlei-info-analyze | `skills/amlei-info-analyze/` | 已收集信息的结构化分析 |
| amlei-git-gh | `skills/amlei-git-gh/SKILL.md` | Git commit / push / PR 工作流 |
| amlei-story-generator | `skills/amlei-story-generator/` | 故事 / 长文生成 |
| amlei-md2img | `skills/amlei-md2img/` | markdown → 图片 |
| amlei-academic-ref-retrieval | `skills/amlei-academic-ref-retrieval/` | 学术文献检索（arXiv / CNKI）|
| amlei-podcast-outline | `skills/amlei-podcast-outline/` | 播客大纲制作（通读全书+联网搜索+分段口播大纲）|

## Publishing

```sh
# 1. bump version in package.json
# 2. verify package.json files array includes all skills/dirs to ship
# 3. npm publish
```

`package.json` `files` array is the **sole source of truth** for what ships.

## Stale CLAUDE.md

`CLAUDE.md` describes 14 skills / 10 agents / 7 hooks / 2 commands — **majority don't exist in this repo**. Treat CLAUDE.md as reference-only; the tracked git files are the actual source.

## What's NOT in this repo

- `agents/` is empty (no tracked agent files)
- No `hooks/` or `commands/` directories
- No CI, no test suite, no formatter config
- `.opencode/skills/` are OpenCode built-in skills (gitignored)
- `.claude/` is gitignored
- **简历 skill 已迁出** —— 不在本仓（见顶部链接）

## SKILL.md naming and conventions

- All owned skills in `skills/` **must** use the `amlei-{}` prefix for their directory and SKILL name (e.g. `amlei-text-polish`, `amlei-story-generator`).
- After modifying any `SKILL.md`, run `skills-ref validate <skill-dir>` to check frontmatter legality and naming conventions.
- When the user asks questions or discusses changes to any `SKILL.md` — do NOT edit the file. Only read and answer. Edits require explicit user confirmation ("go ahead", "write it", etc.).
- **SKILL 与 reference 职责分离，不重复**：触发条件 / 工作流步骤 / "何时做、做什么"只在 `SKILL.md` 写一次；`references/*.md` 只写"怎么做"的详细方法论（公式 / 范式 / 规范 / 示例），开头不复述 SKILL 已有的触发指令。reference 是 SKILL 的展开，不是复述。

## Git rules for this repo

- Do NOT commit/sync `.opencode/`, `.claude/`, `.amlei-skill/`, or `test/` (gitignored)
- Do NOT commit `.docx` or `.pdf` files

## npm publish

Every push to `main` triggers an `npm publish` to update the published package. Bump version in `package.json` before pushing if changes should ship.
