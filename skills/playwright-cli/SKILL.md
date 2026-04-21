---
name: playwright-cli
description: Quick reference guide for Playwright CLI - a command-line tool for browser automation and testing
triggers:
  keywords:
    - playwright
    - playwright-cli
    - playwright cli
    - 浏览器自动化
    - 浏览器测试
  intent:
    - "使用 playwright"
    - "playwright.*命令"
    - "浏览器.*测试"
    - "自动化.*浏览器"
type: domain
enforcement: suggest
priority: medium
---

# Playwright CLI 技能

Playwright CLI 是一个强大的命令行工具，用于浏览器自动化、测试和交互。

## 快速开始

### 安装

```bash
# 安装 CLI
npm install -g @playwright/cli@latest

# 安装技能
playwright-cli install --skills
```

### 基本用法

```bash
# 打开页面
playwright-cli open https://example.com

# 有头模式运行（可见浏览器）
playwright-cli open https://example.com --headed

# 指定浏览器
playwright-cli open --browser=chrome https://example.com
playwright-cli open --browser=firefox https://example.com
playwright-cli open --browser=webkit https://example.com
playwright-cli open --browser=msedge https://example.com
```

## 核心功能

### 元素交互

```bash
# 点击元素
playwright-cli click [selector]
playwright-cli click "role=button[name=Submit]"

# 输入文本
playwright-cli type [selector] [text]

# 填充文本
playwright-cli fill [selector] [text]

# 选择下拉选项
playwright-cli select [selector] [value]

# 勾选/取消勾选
playwright-cli check [selector]
playwright-cli uncheck [selector]

# 悬停
playwright-cli hover [selector]

# 拖拽
playwright-cli drag [from] [to]

# 上传文件
playwright-cli upload [selector] [files]
```

### 定位元素

```bash
# 使用快照获取元素引用
playwright-cli snapshot
playwright-cli click e15  # 使用引用点击

# 使用 CSS 选择器
playwright-cli click "#main > button.submit"

# 使用角色选择器
playwright-cli click "role=button[name=Submit]"

# 组合选择器
playwright-cli click "#footer >> role=button[name=Submit]"
```

### 截图和快照

```bash
# 获取页面快照
playwright-cli snapshot
playwright-cli snapshot --filename=snapshot.json

# 截图
playwright-cli screenshot
playwright-cli screenshot [ref]
playwright-cli screenshot --filename=screenshot.png

# 保存为 PDF
playwright-cli pdf
```

### 导航控制

```bash
# 后退
playwright-cli go-back

# 前进
playwright-cli go-forward

# 刷新
playwright-cli reload
```

### 键盘和鼠标

```bash
# 按键
playwright-cli press [key]  # Enter, ArrowLeft, etc.

# 鼠标移动
playwright-cli mousemove [x] [y]

# 鼠标按键
playwright-cli mousedown [button]
playwright-cli mouseup [button]

# 滚轮
playwright-cli mousewheel [deltaX] [deltaY]
```

### 标签页管理

```bash
# 列出所有标签页
playwright-cli tab-list

# 新建标签页
playwright-cli tab-new [url]

# 选择标签页
playwright-cli tab-select [index]

# 关闭标签页
playwright-cli tab-close [index]
```

### 网络控制

```bash
# 列出网络请求
playwright-cli network

# 模拟网络请求
playwright-cli route [pattern] [opts]

# 列出活动路由
playwright-cli route-list

# 移除路由
playwright-cli unroute [pattern]
```

### 存储状态

```bash
# 保存/加载存储状态
playwright-cli state-save [filename]
playwright-cli state-load [filename]

# Cookie 管理
playwright-cli cookie-list [--domain]
playwright-cli cookie-get [name]
playwright-cli cookie-set [name] [value]
playwright-cli cookie-delete [name]
playwright-cli cookie-clear

# localStorage 管理
playwright-cli localstorage-list
playwright-cli localstorage-get [key]
playwright-cli localstorage-set [key] [value]
playwright-cli localstorage-delete [key]
playwright-cli localstorage-clear
```

### 开发者工具

```bash
# 控制台日志
playwright-cli console [min-level]

# 执行 JavaScript
playwright-cli eval [code] [ref]
playwright-cli run-code [code]

# 追踪记录
playwright-cli tracing-start
playwright-cli tracing-stop

# 视频录制
playwright-cli video-start
playwright-cli video-chapter [name]
playwright-cli video-stop --filename=video.mp4
```

## 会话管理

### 命名会话

```bash
# 创建命名会话
playwright-cli -s=example open https://example.com --persistent

# 列出所有会话
playwright-cli list
```

### 会话控制

```bash
# 关闭所有浏览器
playwright-cli close-all

# 强制关闭所有浏览器进程
playwright-cli kill-all

# 删除会话数据
playwright-cli -s=name delete-data
```

### 配置编码智能体使用特定会话

```bash
PLAYWRIGHT_CLI_SESSION=todo-app claude .
```

## 监控仪表板

```bash
# 打开可视化仪表板
playwright-cli show
```

仪表板提供：
- **会话网格** - 所有活动会话的实时预览
- **会话详情** - 远程控制功能

## 高级配置

### 配置文件

```bash
# 使用配置文件
playwright-cli --config path/to/config.json open example.com
```

CLI 会自动加载 `.playwright/cli.config.json`（如果存在）。

### 浏览器扩展

```bash
# 连接到现有浏览器标签页
playwright-cli open --extension
```

需要安装 Playwright MCP Bridge 浏览器扩展。

## 快速参考

| 操作 | 命令 |
|------|------|
| 安装 CLI | `npm install -g @playwright/cli@latest` |
| 安装技能 | `playwright-cli install --skills` |
| 打开页面 | `playwright-cli open https://example.com` |
| 点击元素 | `playwright-cli click e15` |
| 输入文本 | `playwright-cli type "hello world"` |
| 截屏 | `playwright-cli screenshot` |
| 获取快照 | `playwright-cli snapshot` |
| 有头模式 | `playwright-cli open --headed` |
| 使用 Firefox | `playwright-cli open --browser=firefox` |
| 监控会话 | `playwright-cli show` |

## 资源

- [Playwright CLI 官方文档](https://playwright.cn/docs/getting-started-cli)
- [Playwright 完整文档](https://playwright.cn/)
- [配置文件选项](https://playwright.cn/docs/cli)
