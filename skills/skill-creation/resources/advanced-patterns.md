# Advanced Patterns

## Visual Output Generation

Skills can bundle scripts that generate interactive HTML files opened in a browser:

```yaml
---
name: codebase-visualizer
description: Generate interactive tree visualization of codebase
allowed-tools: Bash(python *)
---
# Codebase Visualizer

Run the visualization script:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
```

This creates `codebase-map.html` and opens it in the browser.
```

Pattern: skill orchestrates, bundled script does heavy lifting. Works for dependency graphs, test coverage reports, API docs, DB schema visualizations.

## Permission Control

**Deny all skills via /permissions:**
```
Skill
```

**Allow specific skills:**
```
Skill(commit)
Skill(review-pr *)
```

**Deny specific skills:**
```
Skill(deploy *)
```

Syntax: `Skill(name)` for exact match, `Skill(name *)` for prefix with any args.

## Nested Directory Auto-Discovery

In monorepos, Claude discovers skills from nested `.claude/skills/`:
```
packages/frontend/.claude/skills/react-patterns/SKILL.md
packages/backend/.claude/skills/api-conventions/SKILL.md
```

## Skills from Added Directories

`--add-dir` flag auto-loads `.claude/skills/` from added directories with live change detection. Other `.claude/` config (subagents, commands) is NOT loaded.

## Hooks Integration

Skills can define lifecycle hooks scoped to the skill's lifetime:

```yaml
---
name: monitored-task
description: Task with pre/post hooks
hooks:
  PreToolUse:
    - command: "echo 'About to use $TOOL_NAME'"
  PostToolUse:
    - command: "echo 'Finished $TOOL_NAME'"
---
```

## Extended Thinking

Include the word "ultrathink" anywhere in skill content to enable extended thinking.

## Sharing Skills

- **Project skills**: Commit `.claude/skills/` to version control
- **Plugins**: Create `skills/` directory in plugin
- **Managed**: Deploy org-wide via managed settings

## Monorepo Tips

For workspace-specific skills, place them in the package's `.claude/skills/`:
```
packages/api/.claude/skills/api-conventions/SKILL.md
packages/web/.claude/skills/react-patterns/SKILL.md
```

Claude auto-discovers skills from the package you're working in.
