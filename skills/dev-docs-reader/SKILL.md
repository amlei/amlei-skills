---
name: dev-docs-reader
description: Read and provide accurate development documentation for any implementation question. Use when user asks how to implement something, what technology to use, or needs technical guidance. Automatically searches local docs/ first, then falls back to web search for official documentation. Works for any technology, framework, API, or library.
---

# Dev Docs Reader

## Purpose

Read and provide accurate development documentation for **any** implementation question, regardless of technology.

**Core Philosophy:**
- No technology limitations - works for any tech stack
- Prioritize local documentation (docs/)
- Fall back to web search for official docs
- Provide accurate, source-based answers

## When to Use

Automatically activates when user asks:
- **Implementation questions**: "怎么实现...", "how to implement...", "如何实现..."
- **Technology choices**: "用什么技术...", "what technology should I use...", "用什么框架..."
- **Documentation requests**: "查看文档", "read docs", "check documentation", "API文档"
- **Technical guidance**: "怎么使用...", "how to use...", "如何使用..."
- **Integration questions**: "怎么集成...", "how to integrate...", "如何对接..."
- **Any development question** that benefits from documentation

**Key phrases that trigger this skill:**
- "怎么实现", "how to implement", "如何实现"
- "用什么", "what technology", "which library"
- "查看文档", "read docs", "check documentation"
- "怎么用", "how to use", "如何使用"
- "集成", "integrate", "对接"

## When to Use

Automatically activates when you mention:
- **UI Libraries**: antd (Ant Design), MUI, puck (page builder)
- **AI/LLM**: OpenAI API, Coze (workflow/conversation), vllm, OCR APIs (monkeyOCR, paddleOCR)
- **WeChat**: wechat, weixin, wxmp (WeChat Mini Program), web-app, qywx (Enterprise WeChat)
- **Cloud Services**: ali (Aliyun SMS), baidu (geocode), vercel (AI SDK)
- **Third-party APIs**: qmapi (QiMa API), openviking
- **Documentation requests**: "read docs", "check documentation", "how to use", "API reference"

**Key phrases that trigger this skill:**
- "阅读文档", "查看文档", "read the docs", "check documentation"
- "怎么使用", "how to use", "API文档", "API reference"
- Technology names: antd, coze, puck, vercel, openai, etc.

## Documentation Sources & Priority

### 📋 Priority Order

```
1️⃣ Local docs/ (Primary)
   ↓ Search for relevant local documentation first
2️⃣ Web Search (Fallback)
   ↓ Search official documentation online
```

### 📁 Local Documentation (Primary Source)

**Search Strategy:**

When user asks about implementing something, first search local `docs/`:

```bash
# Extract key technology/topic from user's question
# User: "怎么实现React表单验证?"
# Key terms: React, 表单验证, form validation

# Search for relevant docs
Glob: "docs/**/*react*/**/*.md"
Glob: "docs/**/*form*/**/*.md"
Glob: "docs/**/*validation*/**/*.md"

# User: "如何使用Coze workflow?"
Glob: "docs/**/*coze*/**/*.md"
Glob: "docs/**/*workflow*/**/*.md"
```

**Best Practices:**
- ✅ Extract key terms from user's question
- ✅ Search multiple related patterns
- ✅ Read all relevant files
- ✅ Provide comprehensive answers

### 🔍 Web Search (Fallback)

**When local docs not found:**

Use `WebSearch` to find official documentation and examples:

```bash
# Search for official documentation
WebSearch: "{technology} official documentation"
WebSearch: "{technology} API reference"
WebSearch: "how to implement {feature} in {technology}"
WebSearch: "{technology} 官方文档"
```

**Example:**
```bash
User: "怎么实现JWT认证?"

Action:
1. Search local: Glob docs/**/*jwt*/**/*.md (not found)
2. Search web: WebSearch "JWT authentication implementation guide"
3. Provide answer based on official docs and examples
```

## How to Use This Skill

### Decision Tree: Documentation Source

```
User Question (any implementation question)
    ↓
Extract key technology/topic terms
    ↓
Search local docs/ for relevant files
(Glob pattern matching)
    ↓
Found relevant docs?
  ↓ YES
  ↓  Read local documentation
  ↓  Provide accurate guidance
  ↓ NO
  ↓  Web search for official docs
  ↓  Provide answer based on search results
```

### Step 1: Extract Key Terms

From user's question, identify relevant technology/topic terms:

**Examples:**
```markdown
User: "怎么实现React表单验证?"
→ Key terms: React, form, validation

User: "如何使用Coze workflow?"
→ Key terms: Coze, workflow

User: "用什么技术实现实时通信?"
→ Key terms: real-time, communication, WebSocket
```

### Step 2: Search Local Documentation

Use multiple search patterns based on extracted terms:

```bash
# Search for each key term
Glob: "docs/**/*{term1}*/**/*.md"
Glob: "docs/**/*{term2}*/**/*.md"
Glob: "docs/**/*{term3}*/**/*.md"

# Also search combined
Glob: "docs/**/*{term1}*{term2}*/**/*.md"

# Example: "React表单验证"
Glob: "docs/**/*react*/**/*.md"
Glob: "docs/**/*form*/**/*.md"
Glob: "docs/**/*validation*/**/*.md"
```

### Step 3: Read & Process Documentation

**If local docs found:**
```bash
Read all relevant .md files
Extract relevant sections
Provide comprehensive answer
```

**If no local docs:**
```bash
WebSearch: "{technology} official documentation"
WebSearch: "how to implement {feature}"
Provide answer based on search results
```

### Step 4: Provide Accurate Guidance

Based on documentation, provide:
- **Implementation approach**: Step-by-step guidance
- **Code examples**: From official documentation
- **Best practices**: As documented
- **API usage**: Endpoints, parameters, response formats
- **References**: Link to specific sources

## Quick Reference

### Technology Discovery Pattern

**When user mentions a technology:**

1. **Use Glob to find docs:**
   ```bash
   Glob "docs/**/*{technology}*/**/*.md"
   ```

2. **Read the discovered files:**
   ```bash
   Read docs/{found-path}/file.md
   ```

3. **Provide accurate guidance based on documentation**

### Reading Documentation Pattern

```markdown
# When user mentions [technology]:

1. **Map to docs path**:
   docs/[category]/[technology]/

2. **List available docs**:
   Use Glob to find all .md files

3. **Read relevant documentation**:
   Use Read to get actual content

4. **Summarize and guide**:
   - Provide key information
   - Include code examples from docs
   - Reference specific files
```

## Examples

### Example 1: Implementation question (local docs found)

**User:** "怎么实现Coze workflow?"

**Action:**
```bash
1. Extract terms: Coze, workflow
2. Search local: Glob "docs/**/*coze*/**/*.md"
3. Found: docs/coze/workflow/*.md
4. Read documentation
5. Provide: API usage, code examples, parameters from docs
```

### Example 2: Technology choice question (no local docs)

**User:** "用什么技术实现实时通信?"

**Action:**
```bash
1. Extract terms: real-time, communication
2. Search local: Glob "docs/**/*websocket*/**/*.md" (not found)
3. WebSearch: "real-time communication technology comparison"
4. Provide: Options like WebSocket, SSE, WebRTC with pros/cons
```

### Example 3: Documentation request

**User:** "查看表单验证的文档"

**Action:**
```bash
1. Extract terms: form, validation
2. Search local: Glob "docs/**/*form*/**/*.md"
3. Search local: Glob "docs/**/*validation*/**/*.md"
4. Read all found files
5. Provide: Comprehensive validation guide from docs
```

### Example 4: Implementation guide (no local docs)

**User:** "如何实现JWT认证?"

**Action:**
```bash
1. Extract terms: JWT, authentication
2. Search local: Glob "docs/**/*jwt*/**/*.md" (not found)
3. WebSearch: "JWT authentication implementation guide"
4. Provide: Step-by-step JWT implementation with code examples
```

## Best Practices

✅ **DO:**
- Always search local docs/ first
- Extract multiple key terms from question
- Use multiple search patterns
- Read all relevant documentation files
- Quote documentation directly
- Provide file references: `[topic](docs/path/file.md)`
- Fall back to WebSearch for official docs
- Keep documentation up-to-date

❌ **DON'T:**
- Guess API signatures or parameters
- Provide information without checking docs
- Skip local docs search
- Rely on memory for API details
- Assume docs haven't changed

## Workflow Summary

```
User asks implementation question
    ↓
Extract key technology/topic terms
    ↓
Search local docs/ (Glob patterns)
    ↓
Found relevant documentation?
    ↓
  YES → Read local docs
    ↓
       Provide accurate guidance
    ↓
  NO  → WebSearch official docs
    ↓
       Provide answer based on search
    ↓
Reference specific sources
```

**Key Principles:**
- 🏠 **Local first**: Always check docs/ first
- 🔍 **Dynamic discovery**: Extract key terms, search patterns
- 📖 **Read actual docs**: Source from documentation
- 🌐 **Web fallback**: Search official docs when needed
- ✅ **Accurate answers**: Based on actual documentation

---

**Status**: ACTIVE - Automatically reads documentation for mentioned technologies
**Docs Location**: `docs/`
**Purpose**: Ensure accurate, documentation-based responses
