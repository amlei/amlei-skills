---
name: git-gh
description: Guide for git commit, push, and PR using gh CLI (GitHub). Use when committing code, pushing to remote, creating pull requests, managing branches, or any git workflow. Covers commit message conventions, push strategies, and PR creation with confirmation gates.
argument-hint: "[回车=commit&push] 1=staged files 2=unstaged files"
disable-model-invocation: true
---
# Git & GitHub Workflow
Use `gh` CLI (GitHub) for all remote operations. Commit and push directly without confirmation. Only PR requires explicit user approval.
## ⚠️ CRITICAL CONSTRAINT
**NEVER automatically commit and push after making edits.**
This skill should ONLY activate when:
- User explicitly asks: "commit", "push", "create PR", "提交", "推送"
- User invokes: `/git-gh` command
- User explicitly requests git operations
**DO NOT:**
- Auto-commit after editing files
- Suggest committing after each change
- Be proactive about git operations
**WAIT for the user to initiate.**
## Interactive Mode
When this skill is invoked, immediately run `git status --short` in the background, then ask the user to choose via `AskUserQuestion`:
**Options:**
| # | Option | Action |
|---|--------|--------|
| 默认/回车 | Commit & Push | Execute full commit + push flow (Section 1 + 2) |
| 1 | Staged Files | Show `git diff --cached --stat` + `git diff --cached`, then ask next action |
| 2 | Unstaged Files | Show `git status --short` + `git diff --stat`, then ask next action |
**Flow after viewing files (option 1 or 2):**
- Ask user: proceed to commit & push / stage or unstage specific files / go back
- After staging/unstaging, loop back to the choice menu
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
5. Present to user for approval — include suggested labels, assignees, reviewers
6. Push with `-u` if needed, then create via `gh pr create`
7. Return the PR URL
### PR Metadata
When creating a PR, suggest and apply labels, assignees, and reviewers:
| Parameter | Flag | Example |
|-----------|------|---------|
| Labels | `--label` | `--label "enhancement,backend"` |
| Assignees | `--assignee` | `--assignee "user1,user2"` |
| Reviewers | `--reviewer` | `--reviewer "user1"` |
| Milestone | `--milestone` | `--milestone "v2.0"` |
| Project | `--project` | `--project "Roadmap"` |
**How to suggest metadata:**
- **Labels**: infer from change type (`feat` → `enhancement`, `fix` → `bug`, `docs` → `documentation`)
- **Assignees**: default to the current user (`@me`) unless the user specifies others
- **Reviewers**: ask the user who should review
**When presenting the PR for approval**, include the metadata:
```
Title: feat: add user login
Labels: enhancement
Assignees: @me
Reviewers: (ask user)
```
**To update an existing PR's metadata:**
```bash
gh pr edit <number> --add-label "enhancement" --add-assignee "username"
```
### gh pr create Template
```bash
gh pr create --title "the title" \
  --label "enhancement" \
  --assignee "@me" \
  --body "$(cat <<'EOF'
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
| Create PR | `gh pr create --title "..." --body "..." --label "..." --assignee "..."` |
| Edit PR metadata | `gh pr edit <n> --add-label "..." --add-assignee "..."` |
| Check existing PRs | `gh pr list` |
| View PR | `gh pr view <number>` |
## Safety Rules
- Never force push to main/master
- Never auto-create PRs
- Never commit secret files (.env, credentials)
- Never use `git add -A` — stage specific files
- Never skip pre-commit hooks (`--no-verify`)
