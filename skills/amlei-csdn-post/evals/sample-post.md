---
title: CSDN 自动发文测试｜复用已登录浏览器（免拷贝 profile）
tags:
  - 自动化
  - Playwright
  - CSDN
  - 效率工具
description: 用 Playwright 通过 CDP 直连你已登录的 Chromium 浏览器（Chrome/Edge 等，开启远程调试开关，免拷贝 profile），自动把 Markdown 发布成 CSDN 博客——正文自动加目录、自动归类标签/专栏、自动填摘要。本文是该流程的一次端到端验证。
visibility: 私密
toc: true
---

# CSDN 自动发文测试

这篇文章由 `amlei-csdn-post` skill 自动发布：读取本地 Markdown，在正文开头插入 `@[toc]` 目录，归类标签与分类专栏，填写摘要，最后通过复用**已登录的浏览器** 驱动 CSDN 网页编辑器完成发布。

## 为什么复用已登录的浏览器

CSDN 没有公开稳定的发文 API，后台接口还带加密签名，逆向极易失效。最稳的方式是直接驱动官方网页编辑器，并通过 CDP 连接你已经登录好的浏览器（任一 Chromium 内核），省去重新登录、绕过验证码。

## 关键步骤

### 1. 开启浏览器远程调试（免拷贝 profile）

在已登录 CSDN 的 Chromium 浏览器（Chrome/Edge/Brave 等）里打开 `<浏览器>://inspect/#remote-debugging`（如 `edge://inspect`、`chrome://inspect`），勾选「Allow remote debugging for this browser instance」。脚本从 `DevToolsActivePort` 读出 WS 端点直连该浏览器，复用现成登录态——无需拷贝 profile、无需重登。

### 2. 正文注入目录

在 Markdown 正文开头单独一行写 `@[toc]`，CSDN 会根据各级标题自动生成可点击的目录——就像本文开头那样。

### 3. 归类与摘要

标签、分类专栏、摘要从 YAML front matter 读取；缺失时由执行 LLM 读正文推断并和用户确认。

## 小结

这是端到端验证发布：目录在、标签在、专栏在、摘要在、可见范围设为私密。如果你能看到这篇文章，说明自动化流程跑通了。
