# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **npm-published Claude Code plugin** - a collection of production-tested skills, agents, hooks, and commands. It is distributed as `amlei-skills` and can be installed via `claude plugin install npm:amlei-skills`.

**What this contains:**
- **Skills** (14): Domain-specific guidelines with bilingual support (Chinese/English)
- **Agents** (10): Autonomous specialists for complex multi-step tasks
- **Hooks** (7): Shell/TypeScript scripts for automation
- **Commands** (2): Custom slash commands

**Key insight:** This is both a working plugin AND a reference library. Components can be used via the plugin OR copied to other projects for customization.

---

## Repository Structure

```
amlei-skills/
├── .claude-plugin/     # Plugin metadata (plugin.json)
├── agents/             # Standalone agent definitions (.md files)
├── commands/           # Custom slash commands (.md files)
├── hooks/              # Shell scripts and TypeScript for automation
├── skills/             # Domain-specific skill directories with resources/
│   ├── skill-rules.json  # Central config for skill activation (reference)
│   └── [skill-name]/    # Individual skill directories
└── package.json        # npm package manifest
```

### Key Files

- **`package.json`**: npm package definition - controls which skills/agents are published
- **`.claude-plugin/plugin.json`**: Plugin metadata for Claude Code
- **`docs/skill-rules.json`**: Reference configuration for skill activation patterns
- **`hooks/skill-activation-prompt.ts`**: TypeScript script that reads skill-rules.json and injects skill suggestions
- **`hooks/post-tool-use-tracker.sh`**: Tracks file changes across sessions to maintain context

---

## Plugin Development Workflow

When developing this plugin itself:

### Local Testing

```bash
# Test locally from plugin directory
claude --plugin-dir .

# Reload after changes (in Claude Code session)
/reload-plugins
```

### Publishing

1. Update version in `package.json`
2. Ensure `package.json` files array includes all skills to publish
3. Run `npm publish`
4. Users install via: `claude plugin install npm:amlei-skills`

### Adding a New Skill

1. Create directory: `skills/your-skill/`
2. Create `SKILL.md` with YAML frontmatter (name, description, triggers)
3. Add `resources/` subdirectory for detailed guides (if needed)
4. Add skill directory to `package.json` files array
5. Test locally with `--plugin-dir .`
6. For activation patterns: Document in skill's SKILL.md (plugin uses frontmatter triggers)

### Modifying Skills/Agents/Commands

1. Read the relevant `SKILL.md` or `.md` file
2. Update content as needed
3. Reload plugins: `/reload-plugins`
4. Test the changes

---

## No Traditional Build/Test Commands

This repository contains **documentation and configuration only**, not executable code.

**There are NO:**
- `npm run build` commands
- Test suites to run
- Linting to perform
- Applications to start

**Instead, the workflow is:**
1. Use components via plugin: `claude plugin install npm:amlei-skills`
2. OR copy agents/skills/hooks/commands to target projects
3. Customize path patterns if copying skills
4. Configure hooks in target project's `.claude/settings.json`

---

## Available Skills

### Domain Skills

#### 1. **skill-developer** (Meta-skill)
**Purpose:** Creating and managing Claude Code skills
**Use when:** Creating skills, modifying skill frontmatter, debugging activation
**Enforcement:** suggest | priority: high

#### 2. **skill-creation** (Meta-skill)
**Purpose:** Guide for creating Claude Code skills following official standards
**Use when:** Creating new skills, writing SKILL.md files, configuring frontmatter
**Enforcement:** suggest | priority: high

#### 3. **backend-dev-guidelines**
**Purpose:** Node.js/Express/TypeScript patterns
**Covers:** Layered architecture, BaseController, Prisma, Sentry, Zod validation
**Enforcement:** suggest | priority: high
**Customization:** ⚠️ Update `pathPatterns` for backend directories

#### 4. **frontend-dev-guidelines**
**Purpose:** React/TypeScript/MUI v7 patterns
**Covers:** Modern React, Suspense, TanStack Router, MUI v7 styling
**Enforcement:** ⚠️ block (guardrail) | priority: high
**Customization:** ⚠️ Update `pathPatterns` + verify React/MUI usage

#### 5. **route-tester**
**Purpose:** Testing authenticated API routes (JWT cookie-based auth)
**Covers:** JWT cookie auth testing, cURL patterns, debugging
**Enforcement:** suggest | priority: high
**Customization:** ⚠️ Requires JWT cookie auth setup

#### 6. **error-tracking**
**Purpose:** Sentry error tracking and monitoring
**Covers:** Sentry v8, error capture, breadcrumbs, performance monitoring
**Enforcement:** suggest | priority: high
**Customization:** ⚠️ Update `pathPatterns` for backend

#### 7. **dev-docs-reader**
**Purpose:** Read accurate documentation for implementation questions
**Language:** Bilingual (Chinese/English) trigger keywords
**Enforcement:** suggest | priority: high

#### 8. **d_system_analyse**
**Purpose:** Senior system analyst for code understanding
**Language:** Bilingual (Chinese/English) trigger keywords
**Enforcement:** suggest | priority: ⚠️ critical
**Note:** Default behavior - search project before answering questions

#### 9. **webapp-testing**
**Purpose:** Web application testing patterns
**Covers:** Playwright for testing web applications
**Enforcement:** suggest | priority: medium

### Utility Skills

#### 10. **git-gh**
**Purpose:** Git commit, push, and PR workflow using gh CLI
**Covers:** Commit conventions, push strategies, PR creation with metadata
**Usage:** `/amlei-skills:git-gh` or auto-activate on git operations
**Enforcement:** suggest | priority: high

#### 11. **resume**
**Purpose:** STAR-based resume writing assistant
**Language:** Chinese (for job application context)
**Covers:** Work experience, project experience, professional skills
**Usage:** `/amlei-skills:resume [目标岗位] [数据路径]`
**Enforcement:** suggest | priority: medium

#### 12. **web-scraper**
**Purpose:** Web scraping with multiple tools
**Covers:** Web reader MCP, Playwright CLI, web search, content extraction
**Usage:** `/amlei-skills:web-scraper URL [description]`
**Enforcement:** suggest | priority: high
**Tools:** Bash, Read, Write, Glob, Grep, webReader, WebSearch

#### 13. **playwright-cli**
**Purpose:** Quick reference for Playwright CLI browser automation
**Covers:** Browser automation, testing, element interaction, screenshots
**Language:** Bilingual (Chinese/English)
**Enforcement:** suggest | priority: medium

#### 14. **skill-developer** (Advanced)
**Purpose:** Advanced skill development patterns and debugging
**Covers:** YAML frontmatter, trigger types, enforcement levels, hooks
**Enforcement:** suggest | priority: high

---

## Available Agents

All agents are **standalone** - just copy the `.md` file to use.

### Architecture & Planning
- **code-architecture-reviewer**: Review for architectural consistency
- **plan-reviewer**: Validate development plans before implementation
- **refactor-planner**: Create comprehensive refactoring strategies

### Code Improvement
- **code-refactor-master**: Plan and execute comprehensive refactoring
- **documentation-architect**: Create comprehensive documentation

### Debugging & Testing
- **frontend-error-fixer**: Debug and fix frontend errors
- **auto-error-resolver**: Automatically fix TypeScript compilation errors
- **auth-route-tester**: Test authenticated API endpoints
- **auth-route-debugger**: Debug authentication issues

### Research
- **web-research-specialist**: Research technical issues online

**Integration complexity:**
- ✅ **Copy as-is**: Most agents (no customization needed)
- ⚠️ **May need paths**: `frontend-error-fixer`, `auto-error-resolver`
- ⚠️ **Requires auth setup**: `auth-route-tester`, `auth-route-debugger`

---

## Available Commands

### route-research-for-testing
**Purpose:** Map edited routes & launch tests
**Usage:** `/amlei-skills:route-research-for-testing [/extra/path …]`
**Allowed tools:** Bash (cat, awk, grep, sort, xargs, sed)
**Model:** sonnet

**What it does:**
1. Combines auto-detected route changes with user-specified paths
2. Outputs JSON with route paths, methods, request/response shapes
3. Launches auth-route-tester sub-agent for testing

### d_system_analyse
**Purpose:** System analysis command (alias for skill)
**Usage:** `/amlei-skills:d_system_analyse`

---

## Integration Workflow for Other Projects

When helping users integrate these components into their projects:

### For Skills
1. Ask about project structure (monorepo vs single-app)
2. Copy skill directory to `.claude/skills/`
3. If the skill uses path triggers (like backend/frontend guidelines), customize paths in skill's SKILL.md or skill-rules.json
4. Verify hooks are installed if using activation system
5. Test activation by editing a relevant file

### For Agents
1. **Read agent file first** to understand any requirements
2. Check for hardcoded paths (`~/git/`, `/root/`, `/Users/`)
3. Copy `.md` file to `.claude/agents/`
4. Update paths if found (use `$CLAUDE_PROJECT_DIR` or relative paths)
5. For auth agents: Ask if they use JWT cookie auth first

### For Hooks
1. **Always start with the two essential hooks** (skill-activation-prompt, post-tool-use-tracker)
2. **Ask before adding Stop hooks** - they can block if misconfigured
3. Copy hook files and set execute permissions
4. Install npm dependencies in hooks directory
5. Add hooks configuration to `.claude/settings.json`
6. Test hook execution manually before relying on it

### Common Mistakes to Avoid
- ❌ Keeping example paths (`blog-api/`, `frontend/`, `auth-service/`)
- ❌ Not asking about monorepo vs single-app structure
- ❌ Copying skill activation rules without customizing path patterns
- ❌ Forgetting to set execute permissions on shell scripts (`chmod +x`)
- ❌ Forgetting to `npm install` in hooks directory
- ❌ Adding Stop hooks without testing them first

---

## Key Architectural Patterns

### The 500-Line Rule
Skills should be under 500 lines total. Use progressive disclosure:
- SKILL.md: Overview and quick reference (50-100 lines)
- resources/: Detailed guides organized by topic
- Each resource file: 30-80 lines on specific subtopics

### Session Tracking for Guardrails
Guardrail skills (enforcement: "block") should track session usage:
- Don't nag repeatedly in same session
- Use `sessionSkillUsed: true` in skipConditions
- Allow file markers like `// @skip-validation`
- Support environment variable overrides

### Auto-Detection Patterns
Hooks should auto-detect project structure:
- Detect frontend/backend by directory names
- Detect package manager (pnpm > npm > yarn)
- Detect TypeScript config location
- Fall back to sensible defaults

### Bilingual Support
Many components support both Chinese and English:
- `d_system_analyse`: Bilingual trigger keywords for system analysis
- `dev-docs-reader`: Bilingual trigger keywords for documentation queries
- `resume`: Chinese-focused resume writing
- `playwright-cli`: Bilingual documentation

---

## Important Notes

### Plugin vs Standalone Use
- **Plugin use**: Install via `claude plugin install npm:amlei-skills` - skills auto-activate via frontmatter triggers
- **Standalone use**: Copy skills/agents to projects - may need to configure activation manually

### Path Pattern Customization
When copying skills with file triggers to other projects:
```json
"pathPatterns": [
  "blog-api/src/**/*.ts",      // ← Example path - customize this!
  "frontend/src/**/*.tsx"      // ← Example path - customize this!
]
```
**Always** update these to match the target project structure.

### Hook Dependencies
The hooks require Node.js and TypeScript:
```json
{
  "dependencies": {
    "@types/node": "^20.11.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.3"
  }
}
```
Run `npm install` in `.claude/hooks/` after copying.

### Agent YAML Frontmatter
Agents use YAML frontmatter for metadata:
```yaml
---
name: agent-name
description: What this agent does
model: opus|sonnet|haiku
color: cyan|blue|green|etc.
---
```

### Skill Frontmatter
Skills use YAML frontmatter for activation:
```yaml
---
name: skill-name
description: What this skill does
triggers:
  keywords: [...]
  intent: [...]
type: domain|guardrail
enforcement: suggest|block|warn
priority: critical|high|medium|low
---
```

---

## Summary

This repository is a **publishable Claude Code plugin** containing production-tested extensions. The dual workflow is:

1. **Plugin use**: Install via npm - skills auto-activate based on frontmatter triggers
2. **Copy to projects**: Customize and integrate skills/agents/hooks into target projects

**Key architectural insight:** Skills use frontmatter for activation (plugin) OR skill-rules.json (standalone integration). The two-hook system (UserPromptSubmit + Stop) enables sophisticated skill auto-activation while maintaining a smooth developer experience through gentle reminders rather than blocking friction.
