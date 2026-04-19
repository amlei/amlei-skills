---
name: skill-creation
description: Guide for creating Claude Code skills following the official Agent Skills open standard. Use when creating new skills, writing SKILL.md files, configuring frontmatter, adding support files, passing arguments, injecting dynamic context, running skills in subagents, or troubleshooting skill issues. Covers skill locations, frontmatter reference, invocation control, tool restrictions, paths filtering, and advanced patterns like fork context and shell injection.
---

# Creating Claude Code Skills

Official guide based on the Claude Code skills documentation. Skills extend what Claude can do via a `SKILL.md` file with instructions that Claude adds to its toolkit.

## Skill Locations

| Location | Path | Scope |
|---|---|---|
| Enterprise | Managed settings | All users in org |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where plugin is enabled |

Priority: enterprise > personal > project. Plugin skills use `plugin-name:skill-name` namespace.

## Skill Directory Structure

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── template.md        # Template for Claude to fill
├── examples/
│   └── sample.md      # Example output
└── scripts/
    └── validate.sh    # Executable scripts
```

Keep SKILL.md under 500 lines. Move details to reference files. Link them from SKILL.md:

```markdown
## Additional resources
- For API details, see [reference.md](reference.md)
- For examples, see [examples.md](examples.md)
```

## Frontmatter Reference

All fields optional. `description` is recommended.

```yaml
---
name: my-skill              # Slash command name (lowercase, hyphens, max 64 chars)
description: What it does   # Claude uses this to decide when to activate
argument-hint: "[issue-number]"  # Autocomplete hint
disable-model-invocation: true   # Only user can invoke (not Claude)
user-invocable: false            # Hide from / menu (background knowledge)
allowed-tools: Read Grep Glob    # Tools allowed without permission prompts
model: sonnet                    # Model override
effort: high                     # Effort level: low, medium, high, max
context: fork                    # Run in isolated subagent
agent: Explore                   # Subagent type for fork context
hooks: {}                        # Lifecycle hooks
paths: "src/**/*.ts"             # Glob: only activate for matching files
shell: powershell                # Shell for backtick commands (bash default)
---
```

## Two Skill Content Types

**Reference content** — knowledge Claude applies inline:
```yaml
---
name: api-conventions
description: API design patterns for this codebase
---
When writing API endpoints:
- Use RESTful naming
- Return consistent error formats
```

**Task content** — step-by-step workflow (add `disable-model-invocation: true`):
```yaml
---
name: deploy
description: Deploy to production
context: fork
disable-model-invocation: true
---
1. Run the test suite
2. Build the application
3. Push to deployment target
```

## Invocation Control

| Frontmatter | User invokes | Claude invokes | Context loading |
|---|---|---|---|
| (default) | Yes | Yes | Description always loaded, full content on invoke |
| `disable-model-invocation: true` | Yes | No | Description NOT loaded, full content on user invoke |
| `user-invocable: false` | No | Yes | Description always loaded, full content on Claude invoke |

## String Replacements

| Variable | Description |
|---|---|
| `$ARGUMENTS` | All arguments passed to skill |
| `$ARGUMENTS[N]` or `$N` | Argument by 0-based index |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing SKILL.md |

## Passing Arguments

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---
Fix GitHub issue $ARGUMENTS following our coding standards.
```

`/fix-issue 123` → "Fix GitHub issue 123 following our coding standards."

Positional: `/migrate-component SearchBar React Vue`
```
Migrate the $0 component from $1 to $2.
```

## Dynamic Context Injection

`` !`command` `` runs shell commands before Claude sees the content:

```yaml
---
name: pr-summary
description: Summarize PR changes
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---
## PR context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request.
```

## Subagent Execution

Add `context: fork` to run in an isolated subagent:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---
Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with file references
```

`agent` options: `Explore`, `Plan`, `general-purpose`, or any custom subagent from `.claude/agents/`.

## Paths Filtering

Limit activation to specific file patterns:

```yaml
---
name: react-patterns
description: React component patterns
paths: "src/components/**/*.tsx,src/pages/**/*.tsx"
---
```

## Quick Creation Checklist

- [ ] Create `.claude/skills/<name>/SKILL.md`
- [ ] Add frontmatter with `name` and `description`
- [ ] Write instructions (under 500 lines)
- [ ] Add reference files for details, link from SKILL.md
- [ ] Test: ask a matching question or run `/skill-name`
- [ ] Verify description includes keywords users would naturally say

## Troubleshooting

**Skill not triggering**: Check description keywords, verify with "What skills are available?", try `/skill-name` directly.

**Triggering too often**: Make description more specific, add `disable-model-invocation: true`.

**Description truncated**: Each entry capped at 250 chars. Lead with key use cases. Raise limit with `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var.

## Reference Files

- [frontmatter-examples.md](resources/frontmatter-examples.md) — Complete frontmatter examples for common skill types
- [advanced-patterns.md](resources/advanced-patterns.md) — Visual output generation, hooks integration, permission control
