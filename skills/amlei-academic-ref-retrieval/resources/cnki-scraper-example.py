#!/usr/bin/env python3
"""知网 CNKI 检索示例 — 按关键词搜索并提取论文元信息.

知网有反爬机制，此脚本演示基础请求 + HTML 解析思路。
实际使用时可能需要处理 cookie / session / 验证码。
"""

import sys
import re
import urllib.parse
from urllib.request import urlopen, Request

SEARCH_URL = (
    "https://kns.cnki.net/kcms2/article/adv search?"
    "dbcode=CJFD&filename=&tab=AdvanceSearch&"
    "keyword={kw}&searchType=AdvanceSearch"
)


def fetch(keyword):
    url = SEARCH_URL.format(kw=urllib.parse.quote(keyword))
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as f:
        return f.read().decode("utf-8", "ignore")


def parse(html):
    """极简示例：从 HTML 提取论文条目（知网页面结构复杂，实际需精细解析）。"""
    papers = []
    # 匹配典型条目模式：标题链接 + 作者 + 来源 + 日期
    blocks = re.findall(
        r'<tr[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>.*?'
        r'<td[^>]*>([^<]+)</td>.*?'
        r'<td[^>]*>([^<]+)</td>.*?'
        r'<td[^>]*>(\d{4})</td>',
        html, re.S
    )
    for href, title, authors, source, year in blocks:
        papers.append({
            "title": title.strip(),
            "authors": authors.strip(),
            "source": source.strip(),
            "year": year,
            "url": "https://kns.cnki.net" + href if href.startswith("/") else href,
        })
    return papers


def format_ref(papers, start=1):
    for i, p in enumerate(papers, start):
        print(f"[{i}] {p['authors']}. {p['title']}[J]. {p['source']}, {p['year']}. {p['url']}")


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "大语言模型"
    html = fetch(kw)
    papers = parse(html)
    format_ref(papers)
