# AGENTS.md

npm-published Claude Code plugin — **4 user-authored skills**, personal resume data, and Python utility scripts. No build/test/lint (doc-only repo).

## Owned skills (`skills/`)

| Skill | Path | Key scripts |
|-------|------|-------------|
| amlei-resume | `skills/amlei-resume/` | `scripts/boss_zhipin.py`, `extract_avatar.py`, `profile.py`, `wrap_preview.py` |
| amlei-story-generator | `skills/amlei-story-generator/` | — |
| amlei-git-gh | `skills/amlei-git-gh/SKILL.md` | — |
| amlei-academic-ref-retrieval | `skills/amlei-academic-ref-retrieval/` | `resources/arxiv-api-example.py`, `cnki-scraper-example.py` |

## Publishing

```sh
# 1. bump version in package.json
# 2. verify package.json files array includes all skills/dirs to ship
# 3. npm publish
```

`package.json` `files` array is the **sole source of truth** for what ships.

## Python scripts quirks

- `boss_zhipin.py` uses **CloakBrowser Python SDK** (dep in `.opencode/package.json`) — login state persisted in `.amlei-skill/resume-gen/boss_state.json`
- `wrap_preview.py` — resume markdown → HTML preview shell
- `profile.py` — personal data store (read/write with confirmation)
- Run scripts from repo root; `boss_zhipin.py` expects `cwd`-relative `.amlei-skill/` dir

## Key state files

- `resume/{姓名}/{求职岗位}/简历.md` — resume output
- `resume/{姓名}/{求职岗位}/jd.md` — job description for target position
- `.amlei-skill/resume-gen/boss_state.json` — Boss直聘 login session
- `skills/amlei-resume/scripts/boss_state.json` — alias copy

## Resume skill workflow (amlei-resume)

1. Check existing `resume/{name}/{role}/简历.md` → import old docx/pdf via `markitdown`
2. Save JD to `resume/{name}/{role}/jd.md`
3. Web search for role positioning and comparable JD requirements
4. Write/revise resume markdown → `wrap_preview.py` → browser preview → export PDF

## Stale CLAUDE.md

`CLAUDE.md` describes 14 skills / 10 agents / 7 hooks / 2 commands — **majority don't exist in this repo**. Treat CLAUDE.md as reference-only; the tracked git files are the actual source.

## What's NOT in this repo

- `agents/` is empty (no tracked agent files)
- No `hooks/` or `commands/` directories
- No CI, no test suite, no formatter config
- `.opencode/skills/` are OpenCode built-in skills (gitignored)
- `.claude/` is gitignored

## SKILL.md naming and conventions

- All owned skills in `skills/` **must** use the `amlei-{}` prefix for their directory and SKILL name (e.g. `amlei-resume`, `amlei-story-generator`).
- After modifying any `SKILL.md`, run `skills-ref validate <skill-dir>` to check frontmatter legality and naming conventions.
- When the user asks questions or discusses changes to any `SKILL.md` — do NOT edit the file. Only read and answer. Edits require explicit user confirmation ("go ahead", "write it", etc.).

## Git rules for this repo

- Do NOT commit/sync `.opencode/`, `.claude/`, `.amlei-skill/`, or `test/` (gitignored)
- Do NOT commit `.docx` or `.pdf` files

## npm publish

Every push to `main` triggers an `npm publish` to update the published package. Bump version in `package.json` before pushing if changes should ship.
