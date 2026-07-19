# amlei-resume

简历全流程助手：写简历、改简历、换岗重定向、导入旧简历、装配 HTML 导出 PDF。

## 触发方式

提及"写简历/改简历/投简历/导入简历/简历排版/导出简历 PDF"等自动触发，或调用 `/amlei-resume`。

## 功能

| 功能 | 说明 |
|------|------|
| **写简历（0→1）** | 从零与用户共创目标岗位简历。先建 profile → 聊目标 → 存 JD → 联网调研 → 挖素材 → 逐节共创 → 用户确认后落盘 |
| **改简历** | 聊项目聊经历挖掘新素材，补充量化成果，换岗重定向（保留原岗版本） |
| **导入旧简历** | .docx / .pdf → markitdown 转 Markdown → 重排格式 → 自动填写 profile |
| **简历评估** | 写/改完成后执行 6 维度强制评估（JD 匹配/成果量化/结构/差异化等），迭代到全部通过 |
| **导出 PDF** | 校验格式 → 选主题（7 套）→ 装配 HTML → 套预览壳 → 浏览器导出 PDF |
| **profile 管理** | 个人资料核心存储（基本信息/技能/项目/偏好/目标公司），写入前经独立评估 agent 把关 |
| **Boss直聘** | 基于 CloakBrowser 的 Boss直聘自动化：登录/搜岗/抓取 JD/批量投递 |

## 工作流

1. 检查 profile 是否存在（`profile.py path`），没有则创建
2. 检查 `resume/{姓名}/{求职岗位}/简历.md`
3. 用户提供 JD → 立即写入 `resume/{姓名}/{求职岗位}/jd.md`
4. 联网搜索岗位人才定位
5. 聊项目挖素材 → `materials.md` 持久化
6. 写/改简历 → 简历评估 → 迭代至通过
7. 选主题 → 校验 → 装配 HTML → `wrap_preview.py` → 浏览器预览导出 PDF

## 关键脚本

- `scripts/profile.py` — 个人资料管理（增/改/查/批量）
- `scripts/validate_resume.py` — 简历格式校验
- `scripts/wrap_preview.py` — 装配 HTML 预览壳
- `scripts/extract_avatar.py` — 从证件照抽取头像
- `scripts/boss_zhipin.py` — Boss直聘自动化

## 产物目录

```
resume/{姓名}/{求职岗位}/
├── 简历.md       # 简历正文
├── jd.md         # 岗位 JD
└── materials.md  # 项目讨论素材
```
