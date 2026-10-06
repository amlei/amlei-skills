# Pipeline contract

## Project files

Human-readable artifacts use Markdown. Machine state uses JSON because the next command reads it.

```text
01_选题/选题推荐.md       topic shortlist with evidence
01_选题/选定选题.md       selected story, timeline, risk
02_旁白/旁白稿.md         narration source for TTS only
02_旁白/narration.json    parsed narration state
02_旁白/标题简介.md       title and description
03_素材/素材清单.md       source evidence and download log
03_素材/visual_pool.json  non-overlapping scene pool
04_TTS/tts_manifest.json  TTS chunks, URLs, local audio, offsets
05_ASR/asr_chunks.json    blind ASR chunks and timelines
06_字幕/blind_cues.json   final cue machine state
06_字幕/字幕.md           human-readable cue review
07_成片/scene_plan.json   unique visual assignment
08_QC/QC报告.md           checklist and results
```

## Model contracts

### TTS

Default:

```text
qwen-audio-3.1-tts-flash
```

Macro chunks are built from sentence boundaries and should stay at or below 420 characters.
Do not send per-sentence requests.

Endpoint:

```http
POST /api/v1/services/audio/tts/SpeechSynthesizer
```

Body:

```json
{
  "model": "qwen-audio-3.1-tts-flash",
  "input": {"text_prompt": "<macro chunk>"},
  "parameters": {
    "voice": "Cherry",
    "text_type": "PlainText",
    "format": "wav",
    "sample_rate": 24000
  }
}
```

### Blind ASR

Default:

```text
qwen-audio-3.1-asr-flash-filetrans
```

Submit the public TTS audio URL:

```http
POST /api/v1/services/audio/asr/transcription
X-DashScope-Async: enable
```

Try this body first:

```json
{
  "model": "qwen-audio-3.1-asr-flash-filetrans",
  "input": {"file_url": "<audio-url>"},
  "parameters": {
    "language_hints": ["zh"],
    "disfluency_removal_enabled": true,
    "timestamp_alignment_enabled": true
  }
}
```

If the backend rejects singular `file_url`, retry once with `file_urls`.

Poll `/api/v1/tasks/<task_id>` until `SUCCEEDED`, then download `transcription_url`.

## Blind cue rules

- ASR text is the final subtitle text.
- TTS script is not read by cue generation.
- Prefer ASR sentence boundaries.
- Add 0.08–0.12s lead and 0.18–0.30s tail.
- Clamp a cue against the next cue start.
- Chinese wrapping target: 16 characters per line, maximum three lines.
- No subtitle background.
- The watermark text is opt-in and user-supplied.
- Before building, ask: “你的防盗水印文本是什么？”
- If supplied, render it top-right.
- If not supplied, render no watermark.
- Store the supplied value and consent in `<project>/.amlei-skill/gossip-video/watermark.md` and `watermark.json`.

## Visual rules

- 1080x1920 output.
- Foreground is fitted without stretching.
- Background is the same source, enlarged/cropped and blurred.
- Background opacity is 70%; equivalently, 30% transparent.
- Every used source interval is globally unique.
- Hard cuts only.
- Crop away native subtitles, logos and tickers.
- No children’s faces.
- Prefer two-person frames for relationship stories.

## Visual pool schema

```json
{
  "sources": [
    {
      "id": "ET",
      "file": "/absolute/path/source.mp4",
      "duration": 215.64,
      "crop": [1138, 640, 400, 100],
      "scenes": [
        {
          "start": 40.0,
          "end": 48.0,
          "tags": ["couple", "red carpet"],
          "clean": true
        }
      ]
    }
  ]
}
```

## QC minimum

- `ffprobe` verifies 1080x1920 and audio.
- `blackdetect` must find no transition black segments.
- Contact sheet at 10-second intervals.
- Cue overlap list must be empty.
- STT replay must be performed on the final narration.
- Frame review must check subtitles, watermark, source logos and repeated frames.
