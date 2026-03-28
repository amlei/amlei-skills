# Claude Code Extensions Showcase

A comprehensive collection of production-tested **skills**, **agents**, **hooks**, and **commands** for Claude Code (claude.ai/code).

> [!NOTE]
> This is a **library of Claude Code extensions** - not a traditional software project. Copy components to your projects to enhance Claude's capabilities.

---

## Quick Start

```bash
# 1. Copy a skill to your project
cp -r skills/backend-dev-guidelines your-project/.claude/skills/

# 2. Copy the skill activation hooks
cp -r hooks/* your-project/.claude/hooks/

# 3. Install hook dependencies
cd your-project/.claude/hooks && npm install

# 4. Set execute permissions
chmod +x your-project/.claude/hooks/*.sh

# 5. Configure in your project's .claude/settings.json
# (see Integration Guide below)
```

---

## What's Included

| Component | Count | Description |
|-----------|-------|-------------|
| **Skills** | 8 | Domain-specific guidelines that auto-activate |
| **Agents** | 10 | Autonomous specialists for complex tasks |
| **Hooks** | 7 | Scripts that run at key workflow points |
| **Commands** | 1 | Custom slash commands |

---

## 📚 Skills

Skills provide domain-specific guidance and best practices. They auto-activate based on keywords, file patterns, and code context.

### Available Skills

| Skill | Purpose | Type | Enforcement |
|-------|---------|------|-------------|
| **[skill-developer](skills/skill-developer/)** | Creating and managing Claude Code skills | Meta | Suggest |
| **[backend-dev-guidelines](skills/backend-dev-guidelines/)** | Node.js/Express/TypeScript patterns | Domain | Suggest |
| **[frontend-dev-guidelines](skills/frontend-dev-guidelines/)** | React/TypeScript/MUI v7 patterns | Guardrail | ⚠️ Block |
| **[route-tester](skills/route-tester/)** | Testing authenticated API routes | Domain | Suggest |
| **[error-tracking](skills/error-tracking/)** | Sentry error tracking patterns | Domain | Suggest |
| **[dev-docs-reader](skills/dev-docs-reader/)** | Read accurate documentation (🇨🇳/🇬🇧) | Domain | Suggest |
| **[d_system_analyse](skills/d_system_analyse/)** | Senior system analyst (🇨🇳/🇬🇧) | Domain | Suggest |
| **[webapp-testing](skills/webapp-testing/)** | Web application testing patterns | Domain | Suggest |

### How Skills Work

Skills activate automatically through a sophisticated hook system:

1. **You type a prompt** or edit a file
2. **Hook analyzes** keywords, intent patterns, file paths, and code content
3. **Relevant skills suggest themselves** or block actions (for guardrails)
4. **Claude uses the skill** to provide domain-specific guidance

### Skill Types

- **Domain Skills**: Comprehensive guidance for specific areas (backend, frontend)
- **Guardrail Skills**: Enforce critical best practices to prevent errors (e.g., MUI v7 compatibility)
- **Meta Skills**: Guide for creating and managing other skills

### Enforcement Levels

- **Suggest**: Skill appears as recommendation, doesn't block
- **Block**: Guardrail - must use skill before proceeding
- **Warn**: Shows warning but allows proceeding

---

## 🤖 Agents

Agents are autonomous Claude instances that handle complex multi-step tasks independently.

### Available Agents

#### Architecture & Planning
- **[code-architecture-reviewer](agents/code-architecture-reviewer.md)** - Review code for architectural consistency
- **[plan-reviewer](agents/plan-reviewer.md)** - Validate development plans before implementation
- **[refactor-planner](agents/refactor-planner.md)** - Create comprehensive refactoring strategies

#### Code Improvement
- **[code-refactor-master](agents/code-refactor-master.md)** - Plan and execute comprehensive refactoring
- **[documentation-architect](agents/documentation-architect.md)** - Create comprehensive documentation

#### Debugging & Testing
- **[frontend-error-fixer](agents/frontend-error-fixer.md)** - Debug and fix frontend errors
- **[auto-error-resolver](agents/auto-error-resolver.md)** - Automatically fix TypeScript errors
- **[auth-route-tester](agents/auth-route-tester.md)** - Test authenticated API endpoints
- **[auth-route-debugger](agents/auth-route-debugger.md)** - Debug authentication issues

#### Research
- **[web-research-specialist](agents/web-research-specialist.md)** - Research technical issues online

### Using Agents

```bash
# 1. Copy an agent to your project
cp agents/code-refactor-master.md your-project/.claude/agents/

# 2. Use it in Claude Code
# Ask: "Use the code-refactor-master agent to reorganize this component folder"
```

**That's it!** Agents are standalone and work immediately.

### Agents vs Skills

| Use Agents When... | Use Skills When... |
|-------------------|-------------------|
| Multi-step autonomous tasks | Inline guidance needed |
| Complex analysis required | Checking best practices |
| Clear end goal | Ongoing development work |
| Example: "Review all controllers" | Example: "Creating a new route" |

---

## 🪝 Hooks

Hooks are scripts that run at specific points in Claude's workflow, enabling automation and context awareness.

### Essential Hooks

| Hook | Event | Purpose | Complexity |
|------|-------|---------|------------|
| **skill-activation-prompt** | UserPromptSubmit | Auto-suggest relevant skills | ✅ Plug & play |
| **post-tool-use-tracker** | PostToolUse | Track file changes for context | ✅ Plug & play |

### Optional Hooks

| Hook | Event | Purpose | Complexity |
|------|-------|---------|------------|
| **error-handling-reminder** | Stop | Remind about error handling | ✅ Plug & play |
| **stop-build-check-enhanced** | Stop | TypeScript compilation check | ⚠️ Requires customization |
| **trigger-build-resolver** | Stop | Auto-launch error resolver | ⚠️ Depends on tsc-check |

### Hook Events

- **UserPromptSubmit**: Before Claude sees your prompt
- **PreToolUse**: Before a tool executes
- **PostToolUse**: After a tool completes
- **Stop**: When Claude finishes responding

### Installing Hooks

```bash
# 1. Copy hooks to your project
cp -r hooks/* your-project/.claude/hooks/

# 2. Set execute permissions
chmod +x your-project/.claude/hooks/*.sh

# 3. Install dependencies
cd your-project/.claude/hooks
npm install

# 4. Add to .claude/settings.json
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
    ]
  }
}
```

---

## ➗ Commands

Custom slash commands for specific workflows.

### Available Commands

- **[route-research-for-testing](commands/route-research-for-testing.md)** - Map edited routes and launch tests

```bash
# Usage
/route-research [/extra/path …]
```

---

## Integration Guide

### For Skills

1. **Ask about project structure** (monorepo vs single-app)
2. **Copy skill directory** to `.claude/skills/`
3. **Update `skill-rules.json`** with your paths:
   ```json
   {
     "skills": {
       "backend-dev-guidelines": {
         "fileTriggers": {
           "pathPatterns": [
             "YOUR_BACKEND_PATH/**/*.ts"  // ← Update this!
           ]
         }
       }
     }
   }
   ```
4. **Verify hooks are installed**
5. **Test activation** by editing a relevant file

### For Agents

1. **Read the agent file** to understand requirements
2. **Check for hardcoded paths** (`~/git/`, `/root/`, `/Users/`)
3. **Copy `.md` file** to `.claude/agents/`
4. **Update paths** if needed (use `$CLAUDE_PROJECT_DIR`)
5. **For auth agents**: Verify JWT cookie auth setup

### For Hooks

1. **Start with essential hooks** (skill-activation-prompt, post-tool-use-tracker)
2. **Ask before adding Stop hooks** - they can block if misconfigured
3. **Copy and set permissions**
4. **Install dependencies** (`npm install` in hooks directory)
5. **Test manually** before relying on them

---

## Common Integration Mistakes

❌ **Keeping example paths** (`blog-api/`, `frontend/`, `auth-service/`)
❌ **Not asking about project structure** (monorepo vs single-app)
❌ **Copying skill-rules.json without customization**
❌ **Forgetting execute permissions** (`chmod +x`)
❌ **Forgetting npm install** in hooks directory
❌ **Adding Stop hooks without testing**

---

## Architecture

### The Two-Hook System

Skills auto-activate through two complementary hooks:

1. **UserPromptSubmit Hook** (Proactive)
   - Runs BEFORE Claude sees your prompt
   - Analyzes keywords + intent patterns + file context
   - Injects skill suggestions into Claude's context

2. **Stop Hook** (Gentle Reminders)
   - Runs AFTER Claude finishes responding
   - Analyzes edited files for risky patterns
   - Shows reminders without blocking

**Philosophy**: Gentle reminders maintain code quality without workflow friction.

### Skill Activation Triggers

Skills activate through multiple trigger types:

- **Keywords**: Simple word matching
- **Intent Patterns**: Regex patterns matching user intent
- **File Path Patterns**: Glob patterns for edited files
- **Content Patterns**: Regex within file contents
- **Skip Conditions**: Session tracking, file markers, env vars

### The 500-Line Rule

Skills follow progressive disclosure:
- SKILL.md: Overview and quick reference (50-100 lines)
- resources/: Detailed guides by topic
- Each resource: 30-80 lines on specific subtopics

---

## Bilingual Support

Some components support both Chinese and English:

- **d_system_analyse**: System analysis with bilingual keywords
- **dev-docs-reader**: Documentation queries in both languages

---

## Requirements

- Claude Code (claude.ai/code)
- Node.js 18+ (for hooks)
- TypeScript 5.3+ (for hooks compilation)

---

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Guide for Claude Code instances working in this repo
- **[skills/README.md](skills/README.md)** - Detailed skills documentation
- **[agents/README.md](agents/README.md)** - Detailed agents documentation
- **[hooks/README.md](hooks/README.md)** - Detailed hooks documentation
- **[hooks/CONFIG.md](hooks/CONFIG.md)** - Hook configuration guide

---

## Contributing

This is a showcase/library repository. Contributions welcome:

1. **New Skills**: Follow the [skill-developer](skills/skill-developer/) guide
2. **New Agents**: Create `.md` files with YAML frontmatter
3. **New Hooks**: Document in hooks README with complexity level
4. **Improvements**: Update documentation, fix typos, enhance examples

---

## License

This collection is provided as-is for educational and commercial use.

---

## Quick Reference

### What do I need?

| If you want to... | Use... |
|-------------------|--------|
| Add backend routes | `backend-dev-guidelines` skill |
| Create React components | `frontend-dev-guidelines` skill |
| Test authenticated routes | `route-tester` skill + `auth-route-tester` agent |
| Refactor code organization | `code-refactor-master` agent |
| Review architecture | `code-architecture-reviewer` agent |
| Fix TypeScript errors | `auto-error-resolver` agent |
| Create documentation | `documentation-architect` agent |
| Setup error tracking | `error-tracking` skill |
| Create custom skills | `skill-developer` skill |
| Understand codebase | `d_system_analyse` skill |

---

## Support

For detailed integration instructions, see:
- **[CLAUDE.md](CLAUDE.md)** - For Claude Code instances
- Individual component README files
- [hooks/CONFIG.md](hooks/CONFIG.md) - Hook customization

---

**Made with ❤️ for the Claude Code community**
