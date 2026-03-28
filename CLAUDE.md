# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **collection of Claude Code extensions** - a showcase/library of custom skills, agents, hooks, and commands for Claude Code. It is NOT a traditional software project with build artifacts or a deployed application.

**What this contains:**
- **Skills** (8): Domain-specific guidelines that auto-activate based on context
- **Agents** (10): Autonomous specialists for complex multi-step tasks
- **Hooks** (7): Shell/TypeScript scripts that run at specific Claude workflow points
- **Commands** (1): Custom slash command for route testing

**Key insight:** All components are designed to be copied to other projects. They work standalone or in combination.

---

## Repository Structure

```
amlei-skills/
├── agents/           # Standalone agent definitions (.md files)
├── commands/         # Custom slash commands (.md files)
├── hooks/            # Shell scripts and TypeScript for automation
├── skills/           # Domain-specific skill directories with resources/
└── skills/skill-rules.json  # Central configuration for skill activation
```

### Key Files

- **`skills/skill-rules.json`**: Central configuration controlling when skills auto-activate via keywords, intent patterns, file paths, and content patterns
- **`hooks/skill-activation-prompt.ts`**: TypeScript script that reads skill-rules.json and injects skill suggestions into Claude's context
- **`hooks/post-tool-use-tracker.sh`**: Tracks file changes across sessions to maintain context

---

## No Traditional Build/Test Commands

This repository contains **documentation and configuration only**, not executable code.

**There are NO:**
- `npm run build` commands
- Test suites to run
- Linting to perform
- Applications to start

**Instead, the workflow is:**
1. Copy agents/skills/hooks/commands to target projects
2. Customize path patterns in skill-rules.json
3. Configure hooks in target project's `.claude/settings.json`
4. Use the extensions during development

---

## Architecture: Two-Hook Skill Activation System

Skills auto-activate through a sophisticated hook-based system:

### 1. UserPromptSubmit Hook (`skill-activation-prompt.ts`)
- **Runs:** BEFORE Claude sees user's prompt
- **Purpose:** Analyzes prompt + file context → suggests relevant skills
- **Method:** Reads `skill-rules.json`, matches triggers, injects suggestions via stdout

### 2. Stop Hook (`error-handling-reminder.ts`)
- **Runs:** AFTER Claude finishes responding
- **Purpose:** Gentle reminders for error handling self-assessment
- **Method:** Analyzes edited files for risky patterns, displays reminder if needed

**Philosophy (2025-10-27):** Moved from blocking PreToolUse to gentle reminders - maintains code quality awareness without workflow friction.

---

## Skill Activation Configuration

Skills activate via `skill-rules.json` using multiple trigger types:

### Trigger Types
1. **Keywords** - Simple word matching in user prompts
2. **Intent Patterns** - Regex patterns matching user intent
3. **File Path Patterns** - Glob patterns matching edited files
4. **Content Patterns** - Regex patterns within file contents
5. **Skip Conditions** - Session tracking, file markers, environment variables

### Enforcement Levels
- **`suggest`**: Skill appears as recommendation, doesn't block
- **`block`**: Guardrail - must use skill before proceeding
- **`warn`**: Shows warning but allows proceeding

### Skill Types
- **`domain`**: Comprehensive guidance for specific areas (backend, frontend)
- **`guardrail`**: Enforces critical best practices to prevent errors

### Priority Levels
- **`critical`**: Always trigger when matched
- **`high`**: Trigger for most matches
- **`medium`**: Trigger for clear matches
- **`low`**: Optional - trigger only for explicit matches

---

## Available Skills

### 1. **skill-developer** (Meta-skill)
**Purpose:** Creating and managing Claude Code skills
**Use when:** Creating skills, modifying skill-rules.json, debugging activation
**Enforcement:** suggest | priority: high

### 2. **backend-dev-guidelines**
**Purpose:** Node.js/Express/TypeScript patterns
**Covers:** Layered architecture, BaseController, Prisma, Sentry, Zod validation
**Enforcement:** suggest | priority: high
**Customization:** ⚠️ Update `pathPatterns` for backend directories

### 3. **frontend-dev-guidelines**
**Purpose:** React/TypeScript/MUI v7 patterns
**Covers:** Modern React, Suspense, TanStack Router, MUI v7 styling
**Enforcement:** ⚠️ block (guardrail) | priority: high
**Customization:** ⚠️ Update `pathPatterns` + verify React/MUI usage

### 4. **route-tester**
**Purpose:** Testing authenticated API routes (JWT cookie-based auth)
**Covers:** JWT cookie auth testing, cURL patterns, debugging
**Enforcement:** suggest | priority: high
**Customization:** ⚠️ Requires JWT cookie auth setup

### 5. **error-tracking**
**Purpose:** Sentry error tracking and monitoring
**Covers:** Sentry v8, error capture, breadcrumbs, performance monitoring
**Enforcement:** suggest | priority: high
**Customization:** ⚠️ Update `pathPatterns` for backend

### 6. **dev-docs-reader**
**Purpose:** Read accurate documentation for implementation questions
**Language:** Bilingual (Chinese/English) trigger keywords
**Enforcement:** suggest | priority: high

### 7. **d_system_analyse**
**Purpose:** Senior system analyst for code understanding
**Language:** Bilingual (Chinese/English) trigger keywords
**Enforcement:** suggest | priority: ⚠️ critical
**Note:** Default behavior - search project before answering questions

### 8. **webapp-testing**
**Purpose:** Web application testing patterns
**Enforcement:** suggest | priority: (not specified in config)

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

## Available Hooks

### Essential Hooks (Start Here)

1. **skill-activation-prompt** (UserPromptSubmit)
   - **Purpose:** Auto-suggest skills based on prompt + file context
   - **Critical:** This is THE hook that enables skill auto-activation
   - **Files:** `skill-activation-prompt.sh`, `skill-activation-prompt.ts`
   - **Customization:** ✅ None - reads skill-rules.json automatically

2. **post-tool-use-tracker** (PostToolUse)
   - **Purpose:** Track file changes for context maintenance
   - **Matcher:** Edit|MultiEdit|Write tools
   - **Customization:** ✅ None - auto-detects project structure

### Optional Hooks

3. **error-handling-reminder** (Stop)
   - **Purpose:** Gentle reminders for error handling self-assessment
   - **Files:** `error-handling-reminder.sh`, `error-handling-reminder.ts`
   - **Customization:** ✅ None needed

4. **stop-build-check-enhanced** (Stop)
   - **Purpose:** TypeScript compilation check when user stops
   - **Customization:** ⚠️⚠️⚠️ Heavy - configured for multi-service monorepo

5. **trigger-build-resolver** (Stop)
   - **Purpose:** Auto-launch build-error-resolver agent on compilation failure
   - **Depends on:** tsc-check hook working correctly

### Hook Installation

```bash
# Copy hooks to target project
cp -r hooks/* your-project/.claude/hooks/

# Set execute permissions
chmod +x your-project/.claude/hooks/*.sh

# Install TypeScript dependencies
cd your-project/.claude/hooks
npm install

# Compile TypeScript
npx tsc
```

### Configure in target project's `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/skill-activation-prompt.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-tracker.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/error-handling-reminder.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Available Commands

### route-research-for-testing
**Purpose:** Map edited routes & launch tests
**Usage:** `/route-research [/extra/path …]`
**Allowed tools:** Bash (cat, awk, grep, sort, xargs, sed)
**Model:** sonnet

**What it does:**
1. Combines auto-detected route changes with user-specified paths
2. Outputs JSON with route paths, methods, request/response shapes
3. Launches auth-route-tester sub-agent for testing

---

## Integration Workflow for Other Projects

When helping users integrate these components into their projects:

### For Skills
1. Ask about project structure (monorepo vs single-app)
2. Copy skill directory to `.claude/skills/`
3. Update `pathPatterns` in `skill-rules.json` to match their paths
4. Verify hooks are installed and working
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
- ❌ Copying `skill-rules.json` without customizing `pathPatterns`
- ❌ Setting execute permissions on shell scripts (`chmod +x`)
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

---

## Important Notes

### This is a Bilingual Repository
Many components support both Chinese and English:
- `d_system_analyse`: Bilingual trigger keywords for system analysis
- `dev-docs-reader`: Bilingual trigger keywords for documentation queries

### Path Pattern Customization is Critical
The example `pathPatterns` in `skill-rules.json` are for demonstration:
```json
"pathPatterns": [
  "blog-api/src/**/*.ts",      // ← Example path
  "frontend/src/**/*.tsx"      // ← Example path
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

---

## Development Workflow in This Repository

When working on this repository itself:

### Adding a New Skill
1. Create directory: `skills/your-skill/`
2. Create `SKILL.md` with YAML frontmatter
3. Add `resources/` subdirectory for detailed guides
4. Add entry to `skills/skill-rules.json`
5. Test activation by editing a matching file

### Modifying Existing Skills
1. Read the skill's `SKILL.md` and `resources/*.md`
2. Update content as needed
3. Update `skill-rules.json` if changing triggers
4. Document changes in the skill's README if present

### Adding a New Agent
1. Create `agents/your-agent.md`
2. Include YAML frontmatter with name, description, model
3. Provide clear step-by-step instructions
4. Specify expected output format
5. Add to `agents/README.md`

### Modifying Hooks
1. Update shell script or TypeScript source
2. Test manually: `./hook-name.sh`
3. Run TypeScript check: `cd hooks && npx tsc --noEmit`
4. Update documentation in `hooks/README.md` and `hooks/CONFIG.md`

---

## Summary

This repository is a **library of Claude Code extensions** - not a traditional software project. The workflow is:

1. **Copy** agents/skills/hooks/commands to target projects
2. **Customize** path patterns and configurations
3. **Configure** in `.claude/settings.json`
4. **Use** during development for enhanced capabilities

**Key architectural insight:** The two-hook system (UserPromptSubmit + Stop) enables sophisticated skill auto-activation while maintaining a smooth developer experience through gentle reminders rather than blocking friction.
