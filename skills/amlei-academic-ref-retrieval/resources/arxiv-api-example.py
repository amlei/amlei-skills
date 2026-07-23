#!/usr/bin/env python3
"""arXiv API 检索示例 — 按关键词查论文并输出参考文献格式."""

import sys
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.parse import quote

API = "http://export.arxiv.org/api/query?search_query=all:{kw}&start=0&max_results={n}"
NS = {"a": "http://www.w3.org/2005/Atom"}


def fetch(keyword, max_results=10):
    url = API.format(kw=quote(keyword), n=max_results)
    with urlopen(url) as f:
        return ET.fromstring(f.read())


def parse(root):
    papers = []
    for entry in root.findall("a:entry", NS):
        title = entry.find("a:title", NS).text.strip().replace("\n", " ").replace("  ", " ")
        authors = [a.find("a:name", NS).text for a in entry.findall("a:author", NS)]
        published = entry.find("a:published", NS).text[:10]
        link = entry.find("a:id", NS).text
        papers.append({"title": title, "authors": authors, "date": published, "url": link})
    return papers


def format_ref(papers, start=1):
    for i, p in enumerate(papers, start):
        authors = ", ".join(p["authors"])
        year = p["date"][:4]
        print(f"[{i}] {authors}. {p['title']}[J]. arXiv, {year}. {p['url']}")


if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "RAG"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    root = fetch(kw, n)
    papers = parse(root)
    format_ref(papers)
