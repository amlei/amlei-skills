# Frontmatter Examples

Complete examples for common skill types.

## User-Only Task (deploy, commit, send-message)

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
argument-hint: "[environment]"
---
Deploy $ARGUMENTS to production:
1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded
```

## Background Knowledge (conventions, domain context)

```yaml
---
name: legacy-api-context
description: Context about the legacy API system for backward-compatible changes
user-invocable: false
---
When modifying legacy API endpoints:
- v1 endpoints use snake_case JSON keys
- Auth headers use X-Legacy-Token, not Bearer
- Rate limits are per-IP, not per-user
```

## Read-Only Explorer Skill

```yaml
---
name: audit-structure
description: Audit project structure without making changes
allowed-tools: Read Grep Glob
context: fork
agent: Explore
---
Analyze the project structure:
1. Map the directory tree
2. Identify architectural patterns
3. Flag inconsistencies
```

## Multi-Argument Skill

```yaml
---
name: scaffold
description: Scaffold a new module with tests
argument-hint: "<module-name> <layer>"
---
Create module $0 in the $1 layer:
1. Create the module directory
2. Generate the main file
3. Generate the test file
4. Update the index exports
```

## Path-Filtered Skill

```yaml
---
name: prisma-patterns
description: Prisma ORM best practices
paths: "src/db/**/*.ts,prisma/**/*"
---
When writing Prisma queries:
- Always use select to limit fields
- Use transactions for multi-table writes
- Index fields used in where clauses
```

## Dynamic Context with Shell Injection

```yaml
---
name: branch-context
description: Show current branch context and recent changes
allowed-tools: Bash(git *)
---
## Current Branch
- Branch: !`git branch --show-current`
- Last 5 commits: !`git log --oneline -5`
- Changed files: !`git diff --name-only main...HEAD`

Summarize the current work-in-progress based on the above context.
```

## Fork Skill with Custom Agent

```yaml
---
name: security-audit
description: Security audit of code changes
context: fork
agent: general-purpose
allowed-tools: Read Grep Glob Bash(git *)
---
Perform a security audit on the current changes:
1. Get the diff: !`git diff --name-only main...HEAD`
2. Review each changed file for security issues
3. Check for: SQL injection, XSS, secrets in code, insecure defaults
4. Report findings with severity levels
```
