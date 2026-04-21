# Amlei Skills — Claude Code Plugin

A collection of production-tested **skills**, **agents**, and **commands** for [Claude Code](https://claude.ai/code), distributed as a plugin. Bilingual support (Chinese/English).

## Install

```bash
# From npm
claude plugin install npm:amlei-skills

# Or from local directory
claude plugin install /path/to/amlei-skills
```

After install, reload plugins: `/reload-plugins`

## Skills (14)

Invoke as `/amlei-skills:<name>` or let Claude auto-activate based on context.

| Skill | Invocation | Description |
|-------|-----------|-------------|
| **git-gh** | `/amlei-skills:git-gh` | Git commit/push/PR workflow using gh CLI |
| **resume** | `/amlei-skills:resume` | STAR-based resume writing assistant (Chinese) |
| **skill-creation** | `/amlei-skills:skill-creation` | Create Claude Code skills (official standard) |
| **skill-developer** | `/amlei-skills:skill-developer` | Advanced skill development guide |
| **backend-dev-guidelines** | `/amlei-skills:backend-dev-guidelines` | Node.js/Express/TypeScript patterns |
| **frontend-dev-guidelines** | `/amlei-skills:frontend-dev-guidelines` | React/TypeScript/MUI v7 patterns |
| **error-tracking** | `/amlei-skills:error-tracking` | Sentry v8 error tracking integration |
| **route-tester** | `/amlei-skills:route-tester` | Authenticated API route testing |
| **dev-docs-reader** | `/amlei-skills:dev-docs-reader` | Documentation lookup (CN/EN) |
| **d_system_analyse** | `/amlei-skills:d_system_analyse` | Senior system code analyst (CN/EN) |
| **webapp-testing** | `/amlei-skills:webapp-testing` | Web application testing toolkit |
| **web-scraper** | `/amlei-skills:web-scraper` | Web scraping with Playwright & MCP tools |
| **playwright-cli** | `/amlei-skills:playwright-cli` | Playwright CLI quick reference (CN/EN) |

## Agents (10)

Agents are available automatically when the plugin is enabled.

| Agent | Description |
|-------|-------------|
| **code-architecture-reviewer** | Review code for architectural consistency |
| **plan-reviewer** | Validate development plans |
| **refactor-planner** | Create refactoring strategies |
| **code-refactor-master** | Execute comprehensive refactoring |
| **documentation-architect** | Create documentation |
| **frontend-error-fixer** | Debug frontend errors |
| **auto-error-resolver** | Fix TypeScript compilation errors |
| **auth-route-tester** | Test authenticated API endpoints |
| **auth-route-debugger** | Debug authentication issues |
| **web-research-specialist** | Research technical issues online |

## Commands (2)

| Command | Description |
|---------|-------------|
| `/amlei-skills:d_system_analyse` | System analysis command |
| `/amlei-skills:route-research-for-testing` | Map routes and launch tests |

## Quick Reference

| If you want to... | Use |
|-------------------|-----|
| Commit & push code | `/amlei-skills:git-gh` |
| Write a resume | `/amlei-skills:resume` |
| Create a new skill | `/amlei-skills:skill-creation` |
| Add backend routes | `/amlei-skills:backend-dev-guidelines` |
| Build React components | `/amlei-skills:frontend-dev-guidelines` |
| Setup error tracking | `/amlei-skills:error-tracking` |
| Test API routes | `/amlei-skills:route-tester` |
| Understand a codebase | `/amlei-skills:d_system_analyse` |
| Scrape web content | `/amlei-skills:web-scraper` |
| Use Playwright CLI | `/amlei-skills:playwright-cli` |
| Refactor code | `code-refactor-master` agent |
| Review architecture | `code-architecture-reviewer` agent |

## Development

```bash
# Test locally
claude --plugin-dir .

# Reload after changes (in Claude Code session)
/reload-plugins
```

## License

MIT
