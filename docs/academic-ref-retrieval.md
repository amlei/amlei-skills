# academic-ref-retrieval

学术论文参考文献检索与格式输出。根据论文主题拆解技术方向，编写代码从权威数据库爬取真实论文信息。

## 触发方式

提及"写论文/参考文献/查文献/检索论文/reference retrieval"自动触发，或调用 `/academic-ref-retrieval`。

## 工作流

### 1. 技术分片

将论文主题拆解为核心技术关键词。例如"基于大语言模型的校园智能响应 Agent 系统"→ `LLM`, `Agent`, `RAG`, `Prompt Engineering` 等。

### 2. 检索脚本

对每个关键词编写真实检索脚本（非模拟/预设）：

| 数据源 | 方式 | 工具 |
|--------|------|------|
| arXiv | API 查询 | `python3` + `requests` + `xml.etree.ElementTree` |
| 知网 CNKI | HTML 爬取 | `python3` + `requests` + `BeautifulSoup` |
| 维普 | HTML 爬取 | `python3` + `requests` + `BeautifulSoup` |
| 其他（IEEE/DBLP/PubMed） | API 或爬取 | 按需选择 |

### 3. 筛选

- 文献总数不少于用户指定数量
- 英文不少于指定数量
- 仅引用权威期刊/会议/学术专著 — 不引用博文/新闻/公众号

### 4. 输出

标准参考文献格式，每条附 Source URL：

```
[1] 作者. 标题[J]. 期刊, 年份, 卷(期): 页码. https://doi.org/xxx
```

文献类型标识：`[J]` 期刊 / `[C]` 会议 / `[M]` 专著 / `[D]` 学位论文 / `[P]` 专利

## 约束

- 绝对真实 — 不编造任意字段，检索不到的不引用
- 代码先行 — 先编写并执行检索脚本，再整理输出
- 仅权威学术来源

## 资源

- `resources/arxiv-api-example.py` — arXiv API 检索示例
- `resources/cnki-scraper-example.py` — 知网检索示例
