---
name: web-scraper
description: "Web scraper skill - fetches content from URLs using web tools (web fetch, web reader), Playwright CLI, or MCP tools. Supports extracting text, links (including images), and structured data. Saves results to files. Usage: /web-scraper URL [description]"
triggers:
  keywords:
    - web scraper
    - web-scraper
    - 爬虫
    - 抓取网页
    - 网页抓取
    - fetch url
    - scrape website
    - extract web content
  intent:
    - "抓取.*网页"
    - "爬取.*网站"
    - "scrape.*url"
    - "fetch.*website"
    - "extract.*content.*url"
type: domain
enforcement: suggest
priority: high
allowed-tools: Bash Read Write Glob Grep webReader WebSearch
argument-hint: "[URL] [description]"
context: fork
agent: general-purpose
---

# Web Scraper Skill

Fetch and extract content from URLs using web tools.

## Usage

```bash
# Basic usage
/web-scraper https://example.com

# With description of what to extract
/web-scraper https://example.com Extract all article titles and links

# Save to specific file
/web-scraper https://example.com Save content to output/article.md
```

## Available Tools

### 1. Web Reader (MCP)
Extract readable content from web pages.

```bash
# Basic fetch
webReader url="https://example.com"

# With options
webReader url="..." return_format="markdown" retain_images="true"
```

Options:
- `return_format`: "markdown" (default) or "text"
- `retain_images`: true/false (default: true)
- `timeout`: request timeout in seconds (default: 20)
- `no_cache`: disable cache (default: false)
- `with_links_summary`: include links and images summary (default: false)

### 2. Web Search
Search the web for information.

```bash
WebSearch query="search terms"
```

### 3. Playwright CLI
For JavaScript-heavy sites requiring browser automation.

Invoke `/playwright-cli` skill or use:
```bash
# Open page
playwright-cli open https://example.com

# Get page content
playwright-cli eval "document.body.innerText"

# Screenshot
playwright-cli screenshot --filename=screenshot.png
```

## Workflow

1. **Analyze Request**
   - Extract URL from arguments
   - Parse user's extraction requirements

2. **Choose Tool**
   - Static HTML: Use `webReader` (MCP tool)
   - JS-heavy sites: Use `/playwright-cli` skill
   - Web search: Use `WebSearch` (MCP tool)

3. **Fetch Content**
   - Call MCP tools directly (webReader, WebSearch)
   - Or invoke /playwright-cli skill for JS-heavy sites
   - Handle errors gracefully

4. **Process & Save**
   - Format output as requested
   - Save to file using Write tool
   - Report results to user

## Example Patterns

### Extract Article Content
```markdown
User: /web-scraper https://blog.example.com/article Extract main article

Steps:
1. Use webReader url="..." return_format="markdown"
2. Parse returned markdown for article content
3. Save clean article text to article.md
```

### Get All Links (including images)
```markdown
User: /web-scraper https://example.com Get all links

Steps:
1. Use webReader url="..." with_links_summary="true"
2. Extract links and image URLs from response
3. Save to links.json
```

### Screenshot Page
```markdown
User: /web-scraper https://example.com Take screenshot

Steps:
1. Invoke /playwright-cli skill with URL
2. Take screenshot
3. Report screenshot location
```

### Search and Extract
```markdown
User: /web-scraper Search for "AI news" and extract top 5 results

Steps:
1. Use WebSearch query="AI news"
2. Parse search results
3. For each result, use webReader url="..." to fetch content
4. Compile and save to summary.md
```

## Error Handling

- Invalid URL: Report error and ask for valid URL
- Timeout: Suggest increasing timeout or trying /playwright-cli
- Blocked by anti-scraping: Suggest using /playwright-cli skill
- MCP tool unavailable: Fall back to /playwright-cli or WebSearch

## Best Practices

1. **Prefer webReader MCP tool** for static content - faster and cleaner
2. **Use /playwright-cli skill** for JS-heavy sites or complex interactions
3. **Always validate URLs** before fetching
4. **Save large outputs** to files, don't print to console
5. **Report progress** for multi-step operations
6. **Handle errors** gracefully with clear messages

## Troubleshooting

**Tool not available**: If MCP tools (webReader, WebSearch) fail, fall back to:
- /playwright-cli skill for browser automation
- Bash with curl for simple fetching

**Rate limiting**: Add delays between requests:
```bash
sleep 2  # Wait 2 seconds between requests
```

**Content blocked**: Try Playwright with different user-agent or use playwright-cli state to handle cookies.
