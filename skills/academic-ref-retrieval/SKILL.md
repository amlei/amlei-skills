---
name: academic-ref-retrieval
description: 学术论文参考文献检索与格式输出。根据论文主题拆解核心技术，编写脚从权威期刊/数据库(知网、维普、arXiv等)爬取或提取真实论文信息，按标准参考文献格式输出。触发：写论文 / 参考文献 / 查文献 / 检索论文 / 论文参考 / reference retrieval / academic reference。
argument-hint: "USER_DEFINE DIRECTION THEME ENGLISH_PAPER_NUMBER COUNT_NUMBER"
---

# Academic Reference Retrieval

你是一名高知 `{USER_DEFINE}`，你的研究方向是 `{DIRECTION}`，需要写一篇以 `{THEME}` 为题的论文。你的任务是检索权威、真实的参考文献。

## 工作流

### 1. 技术分片

将论文主题拆解、分片，提炼出最核心的技术，同时辅以技术泛化。以技术为导向，分析完成该论文需要使用到什么技术，将其设定为参考文献方向。

**示例：**
> 用户: 写一篇以《基于大语言模型的校园信息智能响应 Agent 系统设计与实现》为题的毕业论文
> 分片: `LLM`, `AI Model`, `Agent`, `Agent Tool`, `RAG`, `Prompt Engineering`, `Context Engineering`

将分片结果作为后续检索关键词。

### 2. 检索脚本

对每个技术关键词，编写代码脚本从官方权威渠道获取真实论文信息。**不得有预设、手动、模拟行为**——必须真实访问并提取数据。

#### 中文期刊源
- **知网 CNKI** (`https://www.cnki.net/`)：优先使用其开放 API 或搜索页面爬取
- **维普** (`https://qikan.cqvip.com/`)：备用中文期刊源

#### 英文期刊源
- **arXiv** (`https://arxiv.org/`)：开放获取，支持 API 批量查询
- 其他开放学术数据库（如 IEEE Xplore 开放论文、ACL Anthology、DBLP、PubMed Central 等）

#### 提取信息

每篇文献需提取：
- **标题** (论文完整标题)
- **作者** (全部作者)
- **期刊/出版社/会议**
- **日期** (发表年份/月份)
- **DOI / URL** (用于引用和核查)

#### 实现方式

- 检索结果为 **HTML**：用 `python3` + `requests` + `BeautifulSoup` (或 `lxml`) 编写爬虫解析
- 检索结果为 **PDF**：用 `python3` + `PyMuPDF` (`fitz`) 或 `pdfplumber` 提取元数据和参考文献
- 优先使用官方 API（如 arXiv API: `http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results=10`）
- arXiv API 返回 XML，用 `xml.etree.ElementTree` 解析

#### 示例脚本片段

```python
# arXiv API 检索
import urllib.request, xml.etree.ElementTree as ET

keyword = "RAG"
url = f"http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results=10"
with urllib.request.urlopen(url) as f:
    root = ET.fromstring(f.read())
ns = {"a": "http://www.w3.org/2005/Atom"}
for entry in root.findall("a:entry", ns):
    title = entry.find("a:title", ns).text.strip().replace("\n", " ")
    authors = [a.find("a:name", ns).text for a in entry.findall("a:author", ns)]
    published = entry.find("a:published", ns).text[:4]
    link = entry.find("a:id", ns).text
    print(f"{', '.join(authors)}. {title}[J]. arXiv, {published}. {link}")
```

### 3. 筛选与格式

- 文献总数：**至少 `{COUNT_NUMBER}` 篇**（含中英文）
- 英文文献：**至少 `{ENGLISH_PAPER_NUMBER}` 篇**
- 以中文文献为主
- **所有参考文献必须来自权威期刊、学术会议论文集或学术专著** — 不得引用网络文章、新闻、博客、微信公众号、非学术网站等

### 4. 输出格式

按标准参考文献格式输出，每条末尾附 Source URL 供核查：

```
[1] 作者1, 作者2, 作者3. 论文标题[J]. 期刊名称, 年份, 卷号(期号): 起止页码. https://doi.org/xxx
[2] Author A, Author B. Paper Title[C]. Proceedings of Conference, Year: 页码. https://arxiv.org/abs/xxxx
```

**文献类型标识：**
- `[J]` — 期刊论文 (Journal)
- `[C]` — 会议论文 (Conference)
- `[M]` — 专著/图书 (Monograph)
- `[D]` — 学位论文 (Dissertation)
- `[P]` — 专利 (Patent)

## 约束

1. **绝对真实**：不得编造作者、标题、出处、页码、DOI — 所有信息必须从检索结果中提取。检索不到的不引用。
2. **代码先行**：必须先编写并执行检索脚本，拿到结果后再整理输出。禁止凭知识或记忆手动列出参考文献。
3. **来源权威**：只从学术期刊、会议论文集、学术专著中引用。行业报告、技术博客、官方文档等仅作为背景参考，不作为参考文献。
4. **数量达标**：总文献数不低于 `{COUNT_NUMBER}`，英文不低于 `{ENGLISH_PAPER_NUMBER}`。不足则更换关键词或扩展检索范围。

## 资源

- `resources/arxiv-api-example.py` — arXiv API 检索示例脚本
- `resources/cnki-scraper-example.py` — 知网检索示例脚本（需处理反爬）
