# amlei-git-gh

Git commit / push / PR 工作流，基于 `gh` CLI (GitHub)。

## 触发方式

用户说"commit/push/create PR/提交/推送"时激活，或调用 `/amlei-git-gh`。

**不会自动提交** — 必须用户主动发起。

## 交互模式

调用后显示菜单：

| 选项 | 行为 |
|------|------|
| 默认/回车 | 直接 commit & push |
| 1 | 查看已暂存文件（diff）→ 继续或调整 |
| 2 | 查看未暂存文件 → 继续或调整 |

## 功能

### Commit

- 自动收集 `git status` + `git diff` + `git log -10` 作为上下文
- 按 `type: summary` 格式写提交信息（feat/fix/refactor/docs/chore/test/style/perf）
- 逐文件 `git add`，不用 `git add -A`

### Push

- 新分支 `git push -u origin <branch>`
- 已有分支 `git push`
- 禁止 force push（除非用户要求）

### PR

- 仅非 main 分支 commit+push 后询问是否创建 PR
- 自动收集 commits + diff，生成 title + body
- 推荐 labels/assignees/reviewers，用户确认后创建
- `gh pr create --title "..." --body "..." --label "..." --assignee "@me"`

## 安全规则

- 不 force push main/master
- 不自动创建 PR
- 不提交 `.env` / credentials
- 不跳过 pre-commit hooks
