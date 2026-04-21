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

## Workflow

1. **Analyze Request**
   - Extract URL from arguments
   - Parse user's extraction requirements

2. **Try Request First (webReader/requests)**
   - Always attempt `webReader` MCP tool first
   - If successful, continue using webReader for all subsequent URLs
   - Faster and more efficient for static content
   - Use `with_links_summary="true"` to extract all links including images

3. **Fallback to Playwright (Only if Request Fails)**
   - Only use `/playwright-cli` skill when:
     - webReader fails (timeout, blocked, JS rendering required)
     - Complex user interactions needed (clicks, form fills, pagination)
   - Once Playwright is used, continue with Playwright for consistency

4. **Process & Save**
   - Format output as requested
   - Save to file using Write tool
   - Report results to user

## Error Handling

- **Invalid URL**: Report error and ask for valid URL
- **webReader timeout/failure**: Automatically fallback to /playwright-cli skill
- **Blocked by anti-scraping**: Use /playwright-cli skill with browser automation
- **MCP tool unavailable**: Fall back to /playwright-cli or Bash with curl
- **Progressive fallback**: Always try webReader first, only switch to Playwright if it fails

## Best Practices

1. **Always try webReader first** - fastest and most efficient for static content
2. **Stick with one method** - if webReader works, use it for all URLs; if you switch to Playwright, continue with Playwright
3. **Only use Playwright when necessary** - JS rendering, complex interactions, or when webReader fails
4. **Always validate URLs** before fetching
5. **Save large outputs** to files, don't print to console
6. **Report progress** for multi-step operations
7. **Handle errors** with graceful fallback to Playwright

## Troubleshooting

**Tool not available**: If MCP tools (webReader, WebSearch) fail, fall back to:
- /playwright-cli skill for browser automation
- Bash with curl for simple fetching

**Rate limiting**: Add delays between requests:
```bash
sleep 2  # Wait 2 seconds between requests
```

**Content blocked**: Try Playwright with different user-agent or use playwright-cli state to handle cookies.

**Progressive Strategy**: Remember the workflow:
1. Always try webReader first
2. If it works, stick with webReader for all subsequent URLs
3. Only switch to Playwright if webReader fails
4. Once switched to Playwright, continue with Playwright