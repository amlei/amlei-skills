---
name: web-scraper
description: Analyze web pages and extract data using Playwright. Use when user provides a URL and wants to scrape/extract data from the website. Automatically triggers for requests like "scrape this URL", "extract data from website", "analyze page structure".
argument-hint: "<URL> [data-extraction-requirements]"
allowed-tools: mcp__playwright__browser_navigate mcp__playwright__browser_snapshot mcp__playwright__browser_run_code mcp__playwright__browser_evaluate mcp__playwright__browser_take_screenshot
context: fork
agent: general-purpose
---

# Web Scraper - 使用 Playwright MCP 提取网页数据

你的任务是使用 Playwright MCP 工具访问用户提供的 URL，分析页面结构，并提取所需数据。

## 立即开始

**用户的请求：** $ARGUMENTS

**目标 URL：** $0
**数据需求：** ${1:-"提取页面主要数据"}

## 执行步骤

### 第 1 步：访问页面

使用 `mcp__playwright__browser_navigate` 工具导航到目标 URL：

```
目标 URL：$0
等待方式：domcontentloaded
超时时间：60000ms
```

### 第 2 步：分析页面结构

使用 `mcp__playwright__browser_snapshot` 工具获取页面结构快照：

```
深度：10
```

分析快照，识别页面主要元素和导航结构。

### 第 3 步：定位目标数据

根据用户的数据需求（$1），从页面快照中识别目标元素的位置和特征。

**常见数据类型识别：**
- 产品列表：查找 `.product`, `.item`, `.card` 等元素
- 文章列表：查找 `article`, `.post`, `.blog-post` 等元素
- 链接列表：查找导航区域的链接元素
- 表格数据：查找 `table`, `.data-table` 等元素
- 价格信息：查找 `.price`, `[data-price]` 等元素

### 第 4 步：提取数据

使用 `mcp__playwright__browser_run_code` 工具编写 JavaScript 代码提取数据。

**代码模板：**
```javascript
async (page) => {
  const data = await page.evaluate(() => {
    // 根据实际页面结构编写选择器
    const items = document.querySelectorAll('.target-selector');

    return Array.from(items).map(item => ({
      // 提取所需字段
      title: item.querySelector('.title')?.textContent.trim(),
      url: item.querySelector('a')?.href,
      // 根据用户需求添加更多字段
    }));
  });

  return {
    total: data.length,
    data: data
  };
}
```

**注意：** 根据步骤 3 中分析的页面结构，调整选择器以匹配实际元素。

### 第 5 步：处理多页数据（如需要）

如果检测到分页或需要访问多个页面，循环执行以下操作：
1. 查找"下一页"按钮
2. 点击并等待页面加载
3. 提取当前页数据
4. 合并到结果集
5. 重复直到没有下一页

### 第 6 步：返回结果

将提取的数据以结构化的 JSON 格式返回给用户：

```json
{
  "source": "$0",
  "timestamp": "当前时间",
  "total": "数据条数",
  "data": [提取的数据]
}
```

## 数据验证

在返回结果前，确保：
- ✅ 数据字段完整（必需字段不为空）
- ✅ URL 格式正确
- ✅ 文本内容已清理（去除多余空格和换行）
- ✅ 数量统计准确

## 错误处理

如果遇到以下情况，提供清晰的错误消息和解决建议：
- 页面加载超时：建议增加超时时间或检查网络连接
- 找不到目标元素：建议查看页面快照，确认选择器
- 数据为空：建议检查页面结构是否变化

## 完成后

询问用户是否需要：
1. 生成独立的 Node.js + Playwright 爬虫脚本
2. 将数据导出为其他格式（CSV、Excel）
3. 继续爬取相关页面

---

**现在开始执行：使用 Playwright MCP 工具访问 $0 并提取数据**
