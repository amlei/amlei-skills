---
name: git-gh
description: Guide for git commit, push, and PR using gh CLI (GitHub). Use when committing code, pushing to remote, creating pull requests, managing branches, or any git workflow. Covers commit message conventions, push strategies, and PR creation with confirmation gates.
disable-model-invocation: true
---

# Git & GitHub Workflow

Use `gh` CLI (GitHub) for all remote operations. Commit and push directly without confirmation. Only PR requires explicit user approval.

## 1. Commit

### Before Committing

Run in parallel to gather context:
- `git status` — untracked and modified files
- `git diff` — staged and unstaged changes
- `git log --oneline -10` — recent commit style

### Commit Message Rules

- Write in **Chinese or English** depending on the project's existing commit style
- Format: `type: short summary` — one line, concise, human-readable
- Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `style`, `perf`
- Focus on **what changed and why**, not how
- No emojis unless user requests

### Good Examples

```
feat: add user login with email verification
fix: resolve race condition in batch processing
refactor: extract validation logic into shared module
docs: update API endpoint descriptions
chore: upgrade dependencies to latest stable
```

### Bad Examples

```
update files                          # too vague
feat: add feature                     # which feature?
wip                                   # meaningless
fix bug                               # what bug?
```

### Steps

1. Gather context (status, diff, recent log) — run in parallel
2. Stage specific files by name (`git add <file>`), avoid `git add -A`
3. Draft commit message based on actual changes
4. Create commit directly
5. Run `git status` to verify

Never commit files that likely contain secrets (.env, credentials).

## 2. Push

### Steps

1. Check if branch tracks a remote: `git branch -vv`
2. If no upstream, push with: `git push -u origin <branch>`
3. If upstream exists: `git push`
4. **Never force push** unless user explicitly requests

### Current Branch Check

After commit, check if current branch is not `main`/`master`. If on a feature branch and commit + push succeeded, proceed to step 3.

## 3. Pull Request

### When to Ask

After a successful commit + push on a **non-main branch**, ask the user:

> Commit and push completed. Would you like to create a pull request?

**Never create a PR automatically.** Always wait for explicit user confirmation.

### When NOT to Ask

- Already on `main` or `master`
- User only asked to commit (not push)
- PR already exists for this branch

### PR Creation Steps

1. Run in parallel to gather full context:
   - `git status`
   - `git diff`
   - `git log main..HEAD --oneline` — all commits on this branch
   - `git diff main...HEAD` — full diff from base
2. Analyze all changes, draft title and body
3. PR title: under 70 chars, concise summary of the change
4. PR body format:

```markdown
## Summary
- Bullet points of key changes (1-3 items)

## Test plan
- Checklist of verification steps

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

5. Present to user for approval
6. Push with `-u` if needed, then create via `gh pr create`
7. Return the PR URL

### gh pr create Template

```bash
gh pr create --title "the title" --body "$(cat <<'EOF'
## Summary
<bullets>

## Test plan
<checklist>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Quick Reference

| Action | Command |
|---|---|
| Check status | `git status` |
| Stage files | `git add <file>` |
| Commit | `git commit -m "msg"` |
| Push (new branch) | `git push -u origin <branch>` |
| Push (existing) | `git push` |
| Create PR | `gh pr create --title "..." --body "..."` |
| Check existing PRs | `gh pr list` |
| View PR | `gh pr view <number>` |

## Safety Rules

- Never force push to main/master
- Never auto-create PRs
- Never commit secret files (.env, credentials)
- Never use `git add -A` — stage specific files
- Never skip pre-commit hooks (`--no-verify`)
