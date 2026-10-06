---
name: amlei-gossip-video
description: 收集核实吃瓜/热点/绯闻话题，并为选定瓜制作 9:16 中文视频。使用线上 Qwen TTS 和 filetrans ASR、无文稿盲字幕、yt-dlp 素材、FFmpeg 硬切合成。当用户要收集吃瓜选题、制作八卦热点视频、生成带来源的绯闻/新闻解说视频、或要求 qwen-audio TTS/ASR 视频流水线时使用；不用于虚构剧情、普通剪辑或无来源爆料。
---

# amlei-gossip-video

制作规则：一个瓜一个视频；事实必须有来源；不传播未证实传闻；不做虚构剧情。

## 核心流水线

```text
收集选题 → 用户选定 → 核实来源 → 写旁白稿 → 线上 TTS → 线上盲 ASR →
自动字幕 cue → 素材池 → 9:16 视频分段 → 字幕/水印 overlay → 合成 → QC
```

默认模型：

```text
TTS: qwen-audio-3.1-tts-flash
ASR: qwen-audio-3.1-asr-flash-filetrans
```

所有模型请求必须通过 `scripts/gossip_video.py` 完成；不要把 API key 写入提示词、日志或交付文件。

## 目录约定

`init` 会创建并落盘以下结构：

```text
<slug>/
  00_项目.md
  01_选题/选题推荐.md
  01_选题/选定选题.md
  02_旁白/旁白稿.md
  02_旁白/标题简介.md
  03_素材/素材清单.md
  03_素材/visual_pool.json
  04_TTS/
  05_ASR/
  06_字幕/
  07_成片/
  08_QC/
.amlei-skill/gossip-video/  本 Skill 的项目级授权/设置
```

人类可读的事实、清单、旁白、运行记录、QC 报告都写 `.md`。JSON 只作为下一步流水线的机器状态。

## 1. 选题与用户确认

先广泛搜索新闻、X、YouTube、微博、小红书等公开来源，写入 `01_选题/选题推荐.md`。每条推荐必须有：

- 最炸点；
- 冲突/狗血点；
- 至少一个可靠来源和链接；
- 素材线索；
- 风险；
- 推荐理由。

只有真消息、已核验热点、有来源绯闻才可推荐。未证实爆料不得进入正片。给出推荐后停下，让用户选择。

## 2. 选定后落盘

把用户选中的瓜写入 `选定选题.md`：

- 核心事件时间线；
- 每条事实和来源；
- 素材线索；
- 开头 3 秒钩子；
- 中段金句；
- 结尾问题；
- 明确不采用的无来源内容。

## 3. 旁白稿

写入 `02_旁白/旁白稿.md`。格式：

```markdown
## S01
第一句完整旁白。

## S02
第二句完整旁白。
```

开头三秒直接给最炸的已核验事实。结尾抛问题引导评论。旁白稿只服务 TTS；后续字幕不得用它修正、对齐或覆盖 ASR 文本。

## 4. 初始化与模型调用

```bash
SKILL=/Users/amlei/Data/codespaces/projects/amlei-skills/skills/amlei-gossip-video

python3 "$SKILL/scripts/gossip_video.py" init \
  --slug "<slug>" --out "<输出根目录>" --title "<项目标题>"

python3 "$SKILL/scripts/gossip_video.py" narration \
  --project "<项目目录>"
```

TTS 会按大段切分，不逐句生成；默认每段上限 420 字：

```bash
python3 "$SKILL/scripts/gossip_video.py" tts \
  --project "<项目目录>" \
  --model qwen-audio-3.1-tts-flash \
  --voice Cherry \
  --chunk-chars 420
```

ASR 使用线上 filetrans 盲转写；优先直接传入 TTS 返回的音频 URL：

```bash
python3 "$SKILL/scripts/gossip_video.py" asr \
  --project "<项目目录>" \
  --model qwen-audio-3.1-asr-flash-filetrans \
  --language zh
```

ASR 只负责文本和时间轴。不要把旁白稿传给 ASR 提示词，也不要用旁白稿修正 ASR 输出。

## 5. 盲字幕

```bash
python3 "$SKILL/scripts/gossip_video.py" cues \
  --project "<项目目录>" \
  --model qwen-audio-3.1-asr-flash-filetrans
```

生成：

- `06_字幕/blind_cues.json`
- `06_字幕/字幕.md`

规则：

- 字幕文本和时间轴来自 ASR；
- 每条 cue 说完整一句或完整语义段；
- 中文约 16 字/行，最多 3 行；
- 不截断英文单词；
- 不用黑色字幕底；
- cue 不重叠、不倒退。

## 6. 素材池与画面

先下载素材到 `03_素材/`，并在 `素材清单.md` 记录来源、链接、时间区间、人物和风险。可用 `yt-dlp`：

```bash
yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" \
  --merge-output-format mp4 \
  -o "03_素材/<source>.mp4" "<URL>"
```

编辑 `03_素材/visual_pool.json`，给每个 source 提供：

```json
{
  "id": "ET",
  "file": "/absolute/path/source.mp4",
  "duration": 215.64,
  "crop": [1138, 640, 400, 100],
  "scenes": [
    {"start": 40.0, "end": 48.0, "tags": ["couple", "red carpet"], "clean": true}
  ]
}
```

规则：

- 视频片段为主，图片/推文截图只点缀；
- 人物之间的瓜优先两人同框；
- 不重复同一画面区间；
- 裁掉原视频字幕、台标和滚动条；
- 不用儿童正脸；
- 9:16 内主体不拉伸：原比例前景 + 同素材毛玻璃背景；
- 背景透明度按 30% 透明处理；
- 镜头直接硬切，不加黑场或淡入淡出。

生成场景计划：

```bash
python3 "$SKILL/scripts/gossip_video.py" plan \
  --project "<项目目录>" \
  --pool "<项目目录>/03_素材/visual_pool.json" \
  --cover "<项目目录>/cover.png"
```

## 7. 合成

```bash
构建前必须先问用户：**防盗水印文本是什么？**  
不要默认使用 `@半页`；那只是当前账号的水印。其它用户必须提供自己的水印。

用户确认启用后：

```bash
python3 "$SKILL/scripts/gossip_video.py" build \
  --project "<项目目录>" \
  --pool "<项目目录>/03_素材/visual_pool.json" \
  --watermark \
  --watermark-text "<用户提供的防盗水印>"

python3 "$SKILL/scripts/gossip_video.py" package \
  --project "<项目目录>" \
  --audio "<final_voice.m4a>" \
  --speed 1.06
```

用户确认会写入：

```text
<项目目录>/.amlei-skill/gossip-video/watermark.json
```

用户未确认时：

```bash
python3 "$SKILL/scripts/gossip_video.py" build \
  --project "<项目目录>" \
  --pool "<项目目录>/03_素材/visual_pool.json"
```
```

第一帧必须是封面：当事人照片 + 大字标题。封面不要出现“AI 拆解”“A1”等制作侧字样。

解读推文时，可在 cue JSON 手工插入 `visual` 卡片：

```json
{
  "visual": {
    "type": "card",
    "path": "/absolute/path/tweet-card.png"
  }
}
```

推文卡片必须有英文原文关键句高亮和中文翻译。

## 8. 交付前 QC

```bash
python3 "$SKILL/scripts/gossip_video.py" qc \
  --project "<项目目录>" \
  --final "<项目目录>/07_成片/成片_1080x1920.mp4"
```

必须检查：

- STT 回听旁白；
- 抽帧检查字幕、水印、素材；
- 无重复素材区间；
- 无黑场；
- 无原视频字幕/台标遮挡主体；
- 无儿童正脸；
- 无拉伸；
- 1080x1920 正式版和 720p 预览都存在；
- 封面大字清晰。

## 9. 安全边界

- 不生成虚构剧情；
- 不把无来源爆料当事实；
- 不使用儿童正脸；
- 不使用未授权素材冒充来源；
- 不在项目文件中保存 API key；
- 不把 TTS 文稿用于字幕修正。

## Watermark consent

Before `build`, ask the user for their own anti-piracy watermark text. Do not assume `@半页`; that value belongs to the skill owner only.

- If the user supplies a watermark → pass `--watermark --watermark-text "<user watermark>"`.
- If the user does not want one → omit both flags.
- If the user replies without a watermark text, ask again before building.

Explicit consent is persisted under:

```text
<project>/.amlei-skill/gossip-video/watermark.json
```

This follows the existing amlei skill data convention: project-local `.amlei-skill/<skill-name>/`.
