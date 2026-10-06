#!/usr/bin/env python3
"""Project, TTS, blind-ASR cue, video build and QC helper for Chinese gossip videos.

All human-readable text artifacts are written as Markdown. JSON files are machine
state used by the next pipeline step. API credentials are never written to disk.

Required CLI dependencies: ffmpeg/ffprobe, Python packages requests and Pillow.
Optional: yt-dlp for downloading source material.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import requests

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = ImageDraw = ImageFont = None

BASE = "https://dashscope.aliyuncs.com/api/v1"
DEFAULT_TTS_MODEL = "qwen-audio-3.1-tts-flash"
DEFAULT_ASR_MODEL = "qwen-audio-3.1-asr-flash-filetrans"
DEFAULT_VOICE = "Cherry"


def die(msg: str, code: int = 2) -> None:
    print(f"[error] {msg}", file=sys.stderr)
    raise SystemExit(code)


def run(cmd: list[str], *, capture: bool = True, timeout: float | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=capture, text=True, timeout=timeout)


def ffprobe_json(path: Path | str) -> dict[str, Any]:
    p = run(["ffprobe", "-v", "error", "-show_entries",
             "format=duration,size:stream=codec_type,width,height,codec_name",
             "-of", "json", str(path)])
    return json.loads(p.stdout)


def duration(path: Path | str) -> float:
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)])
    return float(p.stdout.strip())


def sha256(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def project_dir(path: Path | str) -> Path:
    p = Path(path).expanduser().resolve()
    if not (p / "02_旁白" / "旁白稿.md").exists():
        die(f"不是有效项目目录：{p}（缺少 02_旁白/旁白稿.md）")
    return p


def watermark_consent_path(root: Path) -> Path:
    return root / ".amlei-skill" / "gossip-video" / "watermark.json"


def save_watermark_consent(root: Path, text: str) -> Path:
    """Persist explicit user consent under the project-local .amlei-skill directory."""
    path = watermark_consent_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "enabled": True,
        "text": text,
        "position": "top-right",
        "confirmed_by_user": True,
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_watermark_consent(root: Path) -> dict[str, Any] | None:
    path = watermark_consent_path(root)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def api_key(args: argparse.Namespace) -> str:
    key = args.api_key or os.environ.get("QWEN_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
    if not key and args.api_key_file:
        key = Path(args.api_key_file).expanduser().read_text(encoding="utf-8").strip()
    if not key:
        die("缺少 API key：设置 QWEN_API_KEY/DASHSCOPE_API_KEY 或使用 --api-key-file")
    return key.strip()


def http_json(method: str, url: str, *, key: str, body: dict | None = None,
              timeout: float = 90, headers: dict | None = None) -> tuple[int, dict[str, Any], str]:
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json; charset=utf-8",
         "Connection": "close", **(headers or {})}
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = requests.Request(method, url, data=data, headers=h)
    s = requests.Session()
    try:
        resp = s.send(req.prepare(), timeout=(10, timeout))
        return resp.status_code, _safe_json(resp.text), resp.text
    finally:
        s.close()


def _safe_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def download(url: str, path: Path, timeout: float = 180) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers={"Connection": "close"}, stream=True, timeout=(10, timeout)) as r:
        r.raise_for_status()
        with path.open("wb") as f:
            for block in r.iter_content(1024 * 256):
                if block:
                    f.write(block)


def normalize_audio(src: Path, dst: Path, *, rate: int = 48000, stereo: bool = True) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
         "-ar", str(rate), "-ac", "2" if stereo else "1", "-c:a", "pcm_s16le", str(dst)])


def md_table(rows: list[list[Any]]) -> str:
    if not rows:
        return "|（空）|\n|---|\n"
    head = rows[0]
    out = ["| " + " | ".join(str(x) for x in head) + " |", "|" + "---|" * len(head)]
    for row in rows[1:]:
        out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |")
    return "\n".join(out) + "\n"


def cmd_init(args: argparse.Namespace) -> None:
    root = Path(args.out).expanduser().resolve() / args.slug
    if root.exists() and not args.force:
        die(f"目录已存在：{root}")
    dirs = ["01_选题", "02_旁白", "03_素材", "04_TTS/requests", "04_TTS/responses",
            "05_ASR", "06_字幕", "07_成片", "08_QC"]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)

    write_md(root / "00_项目.md", f"""# {args.title or args.slug}

## 规格锁定

- 画幅：9:16，1080x1920
- 时长：4–6 分钟
- 语言：中文
- TTS：{args.tts_model}
- ASR：{args.asr_model}
- 字幕方式：无文稿盲字幕，不使用旁白稿对齐
- 画面：素材为主，硬切，不重复画面，避开原字幕/台标，不用儿童正脸
- 交付：成片、720p 预览、封面、QC 报告
""")

    write_md(root / "01_选题" / "选题推荐.md", """# 选题推荐

> 规则：只收真消息/有来源的新闻、热点、绯闻；不传播未证实谣言。每个瓜一个视频。

| 优先级 | 标题/人物 | 最炸点 | 冲突/狗血 | 已核验来源 | 素材线索 | 风险 | 推荐 |
|---:|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |

## 用户选择

- 选定编号：
""")

    write_md(root / "01_选题" / "选定选题.md", """# 选定选题

## 核心事件

<!-- 时间线必须使用可核验来源 -->

## 来源清单

| 事实 | 来源 | 链接 | 日期 |
|---|---|---|---|
|  |  |  |  |

## 风险与不采用内容

- 无来源爆料：
- 未经证实传闻：
- 儿童相关画面：不用正脸，优先不用

## 金句与结尾问题

- 开头 3 秒：
- 中段金句：
- 结尾问题：
""")

    write_md(root / "02_旁白" / "旁白稿.md", """# 旁白稿

> 每个标题是 cue id。正文只保留要朗读的文字；不写画面提示、来源说明或制作指令。

## S01

在这里写第一句旁白。开头三秒必须给出最炸的已核验事实。

## S02

继续时间线或冲突。中段可以插入金句。

## S03

结尾抛出问题，引导评论。
""")

    write_md(root / "03_素材" / "素材清单.md", """# 素材清单

> 视频片段为主；图片/截图只做点缀。同一画面不得重复使用。人物瓜优先两人同框。不用儿童正脸。

| 素材 ID | 来源 | 页面/出处 | 下载链接 | 本地文件 | 时间区间 | 画面描述 | 人物 | 可用 | 风险 |
|---|---|---|---|---|---|---|---|---|---|
| ET-01 | Entertainment Tonight |  |  |  |  | 两人同框红毯 |  | 是 | 台标需裁掉 |

## yt-dlp 下载记录

```bash
yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" --merge-output-format mp4 -o "03_素材/source.mp4" "<URL>"
```
""")

    write_json(root / "03_素材" / "visual_pool.json", {
        "sources": [],
        "notes": "每个 source 必须有 file、duration、crop。scene start/end 不得重叠。clean=false 的不使用。"
    })

    write_md(root / "02_旁白" / "标题简介.md", """# 标题与简介

## 视频标题

在这里写平台标题。

## 视频简介

在这里写简介、来源、话题标签。
""")

    write_md(root / "08_QC" / "QC报告.md", """# QC 报告

- [ ] 1080x1920，9:16
- [ ] 时长 4–6 分钟
- [ ] STT 回听完成
- [ ] 抽帧检查完成
- [ ] 无重复素材区间
- [ ] 无黑场
- [ ] 无原视频字幕/台标遮挡主体
- [ ] 无儿童正脸
- [ ] 字幕无黑色背景
- [ ] 若用户提供了水印，右上角水印存在；未提供则为空
- [ ] 封面大字清晰
""")

    print(root)


def parse_narration(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"^##\s+(S\d+|C\d+)\s*$", text, flags=re.I | re.M)
    if len(sections) < 3:
        die("旁白稿缺少 `## S01` 结构")
    out = []
    for i in range(1, len(sections), 2):
        cid = sections[i].upper()
        body = re.sub(r"<[^>]+>", "", sections[i + 1]).strip()
        body = re.sub(r"\s+", "", body)
        if not body:
            continue
        if "[TODO" in body.upper():
            die(f"{cid} 仍有 TODO")
        out.append({"id": cid, "text": body})
    if not out:
        die("旁白稿没有可用正文")
    return out


def cmd_narration(args: argparse.Namespace) -> None:
    root = project_dir(args.project)
    src = root / "02_旁白" / "旁白稿.md"
    rows = parse_narration(src)
    data = {"model_hint": {"tts": args.tts_model, "asr": args.asr_model},
            "mode": "tts_only", "sentences": rows,
            "sha256": hashlib.sha256(src.read_bytes()).hexdigest()}
    write_json(root / "02_旁白" / "narration.json", data)
    chars = sum(len(x["text"]) for x in rows)
    write_md(root / "02_旁白" / "旁白稿.index.md", f"""# 旁白稿索引

- 句数：{len(rows)}
- 字数：{chars}
- 预计 TTS 大段数：约 {(chars + args.chunk_chars - 1) // args.chunk_chars}
- 文本事实源：`旁白稿.md`（仅用于 TTS）
- 字幕事实源：ASR，不使用本文件

{md_table([["ID", "字数", "开头"]] + [[x["id"], len(x["text"]), x["text"][:18]] for x in rows])}
""")
    print(root / "02_旁白" / "narration.json")


def chunk_text(text: str, max_chars: int) -> list[str]:
    parts, buf = [], ""
    sentences = re.split(r"(?<=[。！？；!?;])", text)
    for s in sentences:
        if not s:
            continue
        if len(buf) + len(s) <= max_chars or not buf:
            # 如果单句超长，按逗号硬切
            while len(s) > max_chars:
                cut = max(s.rfind("，", 0, max_chars), s.rfind(",", 0, max_chars), max_chars // 2)
                piece, s = s[:cut + 1], s[cut + 1:]
                if buf:
                    parts.append(buf); buf = ""
                parts.append(piece)
            buf += s
        else:
            parts.append(buf); buf = s
    if buf:
        parts.append(buf)
    return [re.sub(r"\s+", "", x) for x in parts if x.strip()]


def api_key_arg(args: argparse.Namespace) -> str:
    return api_key(args)


def call_tts(text: str, args: argparse.Namespace, key: str, out_wav: Path,
             req_path: Path, resp_path: Path) -> dict[str, Any]:
    if args.model.startswith("qwen-audio"):
        endpoint = f"{BASE}/services/audio/tts/SpeechSynthesizer"
        body = {"model": args.model,
                "input": {"text_prompt": text},
                "parameters": {"voice": args.voice, "text_type": "PlainText",
                               "format": "wav", "sample_rate": args.sample_rate}}
    else:
        endpoint = f"{BASE}/services/aigc/multimodal-generation/generation"
        body = {"model": args.model,
                "input": {"text": text, "voice": args.voice},
                "parameters": {"text_type": "PlainText", "format": "wav",
                               "sample_rate": args.sample_rate}}
    req_path.parent.mkdir(parents=True, exist_ok=True)
    req_path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    last = ""
    for attempt in range(args.retries):
        try:
            code, j, raw = http_json("POST", endpoint, key=key, body=body, timeout=args.timeout)
            resp_path.parent.mkdir(parents=True, exist_ok=True)
            resp_path.write_text(json.dumps({"status_code": code, "body": j, "raw": raw},
                                            ensure_ascii=False, indent=2), encoding="utf-8")
            if code != 200:
                raise RuntimeError(f"HTTP {code}: {raw[:500]}")
            audio = ((j.get("output") or {}).get("audio")
                     or (j.get("output") or {}).get("audio_url")
                     or {})
            if isinstance(audio, str):
                url, data = audio, None
            else:
                url, data = audio.get("url"), audio.get("data")
            import base64
            if data:
                out_wav.write_bytes(base64.b64decode(data))
            elif url:
                download(url, out_wav, timeout=args.download_timeout)
            else:
                raise RuntimeError(f"response has no audio: {raw[:500]}")
            return {"url": url, "bytes": out_wav.stat().st_size}
        except Exception as exc:
            last = str(exc)
            print(f"[warn] TTS attempt {attempt + 1}/{args.retries} failed: {exc}", file=sys.stderr)
            time.sleep(args.retry_wait * (attempt + 1))
    die(f"TTS failed: {last}", 4)


def cmd_tts(args: argparse.Namespace) -> None:
    root = project_dir(args.project)
    rows = parse_narration(root / "02_旁白" / "旁白稿.md")
    text = "".join(x["text"] for x in rows)
    chunks = chunk_text(text, args.chunk_chars)
    key = api_key_arg(args)
    tdir = root / "04_TTS"
    manifest = []
    total_bytes = 0
    log = ["# TTS 运行记录", "", f"- 模型：`{args.model}`", f"- voice：`{args.voice}`",
           f"- 字数：{len(text)}", f"- 大段数：{len(chunks)}", f"- 每段上限：{args.chunk_chars} 字", ""]
    for i, chunk in enumerate(chunks, 1):
        cid = f"{i:03d}"
        raw = tdir / f"chunk_{cid}.wav"
        norm = tdir / f"chunk_{cid}_48k.wav"
        req = tdir / "requests" / f"chunk_{cid}.request.json"
        resp = tdir / "responses" / f"chunk_{cid}.response.md"
        info = call_tts(chunk, args, key, raw, req, resp)
        normalize_audio(raw, norm)
        dur = duration(norm)
        manifest.append({"id": cid, "text": chunk, "audio": str(norm), "source_audio": str(raw),
                         "url": info.get("url"), "duration": dur, "bytes": norm.stat().st_size,
                         "sha256": sha256(norm), "offset": total_bytes})
        total_bytes += dur
        log += [f"## {cid}", "", f"- 字数：{len(chunk)}", f"- 时长：{dur:.3f}s",
                f"- 音频：`{norm}`", f"- URL：`{info.get('url') or 'inline/base64'}`", ""]
    write_json(tdir / "tts_manifest.json", {"model": args.model, "voice": args.voice,
                                            "chunk_chars": args.chunk_chars, "chunks": manifest})
    write_md(tdir / "TTS运行记录.md", "\n".join(log))
    print(tdir / "tts_manifest.json")


def deep_find_sentences(obj: Any) -> list[dict[str, Any]]:
    """Find likely ASR sentence arrays in DashScope transcription payloads."""
    found = []
    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("sentences"), list) and x["sentences"]:
                found.extend(x["sentences"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(obj)
    return found


def cmd_asr(args: argparse.Namespace) -> None:
    root = project_dir(args.project)
    key = api_key_arg(args)
    tman_path = root / "04_TTS" / "tts_manifest.json"
    if args.audio_urls:
        inputs = [{"id": f"{i:03d}", "url": u, "offset": 0.0, "duration": 0.0}
                  for i, u in enumerate(args.audio_urls, 1)]
    elif tman_path.exists():
        tman = read_json(tman_path)
        inputs = [{"id": x["id"], "url": x.get("url"), "offset": x.get("offset", 0.0),
                   "duration": x.get("duration", 0.0)} for x in tman["chunks"]]
        if args.speed and args.speed != 1.0:
            for x in inputs:
                x["offset"] = x.get("offset", 0.0) / args.speed
    else:
        die("没有可用的 TTS URL；请先运行 tts，或用 --audio-url 传入公开音频 URL")
    endpoint = f"{BASE}/services/audio/asr/transcription"
    chunks = []
    log = ["# ASR 运行记录", "", f"- 模型：`{args.model}`", f"- 输入数：{len(inputs)}", ""]
    for item in inputs:
        if not item.get("url"):
            die(f"TTS chunk {item['id']} 没有 URL，无法在线文件转写")
        bodies = [{"model": args.model, "input": {"file_url": item["url"]},
                   "parameters": {"language_hints": args.language,
                                  "disfluency_removal_enabled": True,
                                  "timestamp_alignment_enabled": True}},
                  {"model": args.model, "input": {"file_urls": [item["url"]]},
                   "parameters": {"language_hints": args.language,
                                  "disfluency_removal_enabled": True,
                                  "timestamp_alignment_enabled": True}}]
        submitted = None
        attempts = []
        for bi, body in enumerate(bodies, 1):
            code, j, raw = http_json("POST", endpoint, key=key, body=body, timeout=90)
            attempts.append({"variant": bi, "status": code, "body": j, "raw": raw[:1000]})
            if code == 200:
                submitted = j; break
            time.sleep(1)
        (root / "05_ASR" / f"submit_{item['id']}.json").write_text(
            json.dumps(attempts, ensure_ascii=False, indent=2), encoding="utf-8")
        if submitted is None:
            die(f"ASR submit failed for {item['id']}: {attempts[-1]['raw'][:500]}")
        task = (submitted.get("output") or {}).get("task_id")
        if not task:
            die(f"ASR submit missing task_id: {submitted}")
        status = None
        result = {}
        for i in range(args.polls):
            code, j, raw = http_json("GET", f"{BASE}/tasks/{task}", key=key, timeout=60)
            result = j
            status = (j.get("output") or {}).get("task_status")
            print(f"[asr] {item['id']} poll {i + 1}: {status}", file=sys.stderr)
            if status in ("SUCCEEDED", "FAILED", "CANCELED"):
                break
            time.sleep(args.poll_wait)
        if status != "SUCCEEDED":
            (root / "05_ASR" / f"result_{item['id']}.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            die(f"ASR {item['id']} status={status}")
        tr_url = None
        def find_urls(x):
            nonlocal tr_url
            if isinstance(x, dict):
                if x.get("transcription_url"): tr_url = x["transcription_url"]
                for v in x.values(): find_urls(v)
            elif isinstance(x, list):
                for v in x: find_urls(v)
        find_urls(result)
        if not tr_url:
            die("ASR succeeded but transcription_url missing")
        rawp = root / "05_ASR" / f"transcript_{item['id']}.json"
        download(tr_url, rawp, timeout=120)
        tr = read_json(rawp)
        chunks.append({"id": item["id"], "offset": item.get("offset", 0.0),
                       "duration": item.get("duration", 0.0), "source_url": item["url"],
                       "transcript": tr})
        log += [f"## {item['id']}", "", f"- offset：{item.get('offset', 0):.3f}s",
                f"- task：`{task}`", f"- transcript：`{rawp}`", ""]
    write_json(root / "05_ASR" / "asr_chunks.json", {"model": args.model, "chunks": chunks})
    write_md(root / "05_ASR" / "ASR运行记录.md", "\n".join(log))
    print(root / "05_ASR" / "asr_chunks.json")


def collect_asr_words(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sentences = []
    for chunk in chunks:
        offset = chunk.get("offset", 0.0)
        ss = deep_find_sentences(chunk.get("transcript"))
        for si, s in enumerate(ss):
            words = []
            for w in s.get("words", []) or []:
                text = str(w.get("text", ""))
                if not text:
                    continue
                words.append({"text": text,
                              "punct": w.get("punctuation") or "",
                              "start": (w.get("begin_time", 0) / 1000.0) + offset,
                              "end": (w.get("end_time", 0) / 1000.0) + offset})
            st = (s.get("begin_time", 0) / 1000.0) + offset
            en = (s.get("end_time", 0) / 1000.0) + offset
            if not words:
                text = re.sub(r"\s+", "", s.get("text", ""))
                if not text:
                    continue
                per = max((en - st) / len(text), 0.04)
                words = [{"text": ch, "punct": "", "start": st + i * per,
                          "end": st + (i + 1) * per} for i, ch in enumerate(text)]
            sentences.append({"chunk": chunk.get("id"), "start": st, "end": en, "words": words})
    sentences.sort(key=lambda x: x["start"])
    return sentences


def wrap_text(text: str, width: int = 16, max_lines: int = 3) -> list[str]:
    tokens, buf = [], ""
    for ch in text:
        if re.match(r"[A-Za-z0-9]", ch):
            if buf and (re.match(r"[A-Za-z0-9]", buf[-1]) or buf[-1] in ".-'@"):
                buf += ch
            else:
                if buf: tokens.append(buf)
                buf = ch
        else:
            if buf: tokens.append(buf)
            buf = ""
            tokens.append(ch)
    if buf: tokens.append(buf)
    lines, cur = [], ""
    for tok in tokens:
        if len(cur + tok) <= width or not cur:
            cur += tok
        else:
            lines.append(cur); cur = tok
    if cur: lines.append(cur)
    if len(lines) <= max_lines: return lines
    target = -(-len(text) // max_lines)
    lines, cur = [], ""
    for tok in tokens:
        if cur and len(cur + tok) > target and len(lines) < max_lines - 1:
            lines.append(cur); cur = tok
        else: cur += tok
    if cur: lines.append(cur)
    return lines


def cmd_cues(args: argparse.Namespace) -> None:
    root = project_dir(args.project)
    p = root / "05_ASR" / "asr_chunks.json"
    data = read_json(p)
    if isinstance(data, dict):
        raw_chunks = data.get("chunks", [])
    else:
        raw_chunks = data
    sentences = collect_asr_words(raw_chunks)
    raw_groups = []
    for s in sentences:
        words, start = s["words"], 0
        for j, w in enumerate(words):
            if w["punct"] in ",。！？；;，" and sum(len(x["text"] + x["punct"]) for x in words[start:j + 1]) >= args.min_group_chars:
                raw_groups.append(words[start:j + 1]); start = j + 1
        if start < len(words):
            tail = words[start:]
            if raw_groups and sum(len(x["text"] + x["punct"]) for x in tail) < args.min_group_chars:
                raw_groups[-1].extend(tail)
            else:
                raw_groups.append(tail)
    groups = []
    for g in raw_groups:
        buf = []
        for w in g:
            disp_len = len(w["text"] + w["punct"])
            buf_len = sum(len(x["text"] + x["punct"]) for x in buf)
            if buf and buf_len + disp_len > args.max_group_chars:
                groups.append(buf); buf = []
            buf.append(w)
            if sum(len(x["text"] + x["punct"]) for x in buf) >= args.max_group_chars:
                groups.append(buf); buf = []
        if buf: groups.append(buf)
    cues = []
    for i, words in enumerate(groups, 1):
        text = "".join(x["text"] + x["punct"] for x in words).strip()
        if not text: continue
        start = max(0, words[0]["start"] - args.lead)
        end = words[-1]["end"] + args.tail
        if i < len(groups):
            nxt = groups[i][0]["start"] - 0.04
            end = min(end, max(start + 0.7, nxt))
        if end - start < 0.8: end = start + 0.8
        cues.append({"id": i, "start": round(start, 3), "end": round(end, 3),
                     "text": text, "lines": wrap_text(text, args.line_chars, 3),
                     "mode": "blind_asr", "script_used": False})
    # 后一条起点前移时，保前条不重叠
    for a, b in zip(cues, cues[1:]):
        if a["end"] > b["start"]:
            a["end"] = max(a["start"] + 0.5, b["start"])
    data = {"mode": "blind_asr", "script_used": False, "asr_model": args.model, "cues": cues}
    write_json(root / "06_字幕" / "blind_cues.json", data)
    md = ["# 盲字幕 Cue", "", f"- ASR：`{args.model}`", f"- cue 数：{len(cues)}", "",
          md_table([["ID", "Start", "End", "Text"]] +
                   [[c["id"], f"{c['start']:.3f}", f"{c['end']:.3f}", c["text"]] for c in cues])]
    write_md(root / "06_字幕" / "字幕.md", "\n".join(md))
    print(root / "06_字幕" / "blind_cues.json")


def cmd_plan(args: argparse.Namespace) -> None:
    root = project_dir(args.project)
    cues = read_json(root / "06_字幕" / "blind_cues.json")["cues"]
    pool = read_json(Path(args.pool))
    cover = Path(args.cover).expanduser().resolve()
    plan, used = [], set()
    for i, c in enumerate(cues, 1):
        if i == 1 and cover.exists():
            plan.append({"type": "cover", "path": str(cover)}); continue
        text = c["text"].lower()
        best, best_score = None, -1
        for src in pool.get("sources", []):
            for scene in src.get("scenes", []):
                if scene.get("clean") is False or (src.get("id"), scene["start"]) in used:
                    continue
                if scene["end"] - scene["start"] + 0.2 < c["end"] - c["start"]:
                    continue
                tags = [x.lower() for x in scene.get("tags", [])]
                score = sum(1 for tag in tags if tag in text)
                priority = scene.get("priority", 0)
                if score > best_score or (score == best_score and priority > (best or {}).get("priority", -1)):
                    best = {"type": "source", "source_id": src["id"], "start": scene["start"],
                            "end": scene["end"], "priority": priority}
                    best_score = score
        if best is None:
            candidates = [(src, sc) for src in pool.get("sources", []) for sc in src.get("scenes", [])
                          if sc.get("clean") is not False and (src["id"], sc["start"]) not in used
                          and sc["end"] - sc["start"] + 0.2 >= c["end"] - c["start"]]
            if not candidates: die(f"素材池不足：cue {i}")
            best = {"type": "source", "source_id": candidates[0][0]["id"],
                    "start": candidates[0][1]["start"], "end": candidates[0][1]["end"], "priority": 0}
        used.add((best["source_id"], best["start"]))
        plan.append(best)
    # 可选推文卡片：cue JSON 中手工设置 visual={"type":"card","path":"..."}
    for c, p in zip(cues, plan):
        v = c.get("visual")
        if isinstance(v, dict) and v.get("type") == "card" and v.get("path"):
            p.clear(); p.update({"type": "card", "path": str(Path(v["path"]).expanduser().resolve())})
    write_json(root / "07_成片" / "scene_plan.json", plan)
    rows = [[i, p.get("type"), p.get("source_id", "cover/card"), p.get("start", ""), cues[i - 1]["text"][:30]]
            for i, p in enumerate(plan, 1)]
    write_md(root / "07_成片" / "scene_plan.md", "# Scene Plan\n\n" + md_table(
        [["Cue", "Type", "Source", "Start", "Text"]] + rows))
    print(root / "07_成片" / "scene_plan.json")


def make_overlay(path: Path, cue: dict[str, Any], watermark: str | None = None, size: tuple[int, int] = (1080, 1920)) -> None:
    if Image is None:
        die("Pillow 未安装：pip install pillow")
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    candidates = ["/System/Library/Fonts/Hiragino Sans GB.ttc",
                  "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    font_path = next((x for x in candidates if Path(x).exists()), None)
    if not font_path: die("未找到可用 CJK 字体")
    f = ImageFont.truetype(font_path, 56)
    wm = ImageFont.truetype(font_path, 41)
    if watermark:
        d.text((size[0] - 52, 52), watermark, font=wm, fill=(255, 255, 255, 215),
               anchor="ra", stroke_width=4, stroke_fill=(0, 0, 0, 200))
    lines = cue.get("lines") or wrap_text(cue["text"])
    blocks = []
    for line in lines:
        bb = d.textbbox((0, 0), line, font=f)
        blocks.append((line, bb[2] - bb[0], bb[3] - bb[1], bb[1]))
    lh = 82; y = size[1] - 220 - (len(lines) * lh - 12)
    for line, w, h, off in blocks:
        d.text(((size[0] - w) // 2, y - off - 2), line, font=f, fill=(255, 255, 255, 255),
               stroke_width=4, stroke_fill=(0, 0, 0, 220))
        y += lh
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def build_image(out: Path, dur: float, inp: Path, bg_alpha: float = 0.7) -> None:
    fg_alpha = 1.0 - bg_alpha
    f = (f"[0:v]split=2[bgsrc][fgsrc];"
         f"[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
         f"gblur=sigma=28,eq=brightness=-0.08,format=rgba,colorchannelmixer=aa={fg_alpha}[bgalpha];"
         f"color=c=black:s=1080x1920:r=30,trim=duration={dur + 0.2:.3f},setpts=PTS-STARTPTS[black];"
         f"[black][bgalpha]overlay=0:0[bgfinal];"
         f"[fgsrc]scale=1080:1920:force_original_aspect_ratio=decrease,"
         f"tpad=stop_mode=clone:stop_duration=10[fgfinal];"
         f"[bgfinal][fgfinal]overlay=(W-w)/2:(H-h)/2,fps=30,setsar=1[v]")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-t", f"{dur + 0.1:.3f}",
         "-i", str(inp), "-filter_complex", f, "-map", "[v]", "-t", f"{dur:.3f}", "-r", "30", "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", str(out)])


def build_source(out: Path, dur: float, inp: Path, start: float, crop: tuple[int, int, int, int]) -> None:
    w, h, x, y = crop
    f = (f"[0:v]crop={w}:{h}:{x}:{y},split=2[bgsrc][fgsrc];"
         f"[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
         f"gblur=sigma=28,eq=brightness=-0.08,format=rgba,colorchannelmixer=aa=0.7[bgalpha];"
         f"color=c=black:s=1080x1920:r=30,trim=duration={dur + 0.2:.3f},setpts=PTS-STARTPTS[black];"
         f"[black][bgalpha]overlay=0:0[bgfinal];"
         f"[fgsrc]scale=1080:1920:force_original_aspect_ratio=decrease,"
         f"tpad=stop_mode=clone:stop_duration=10[fgfinal];"
         f"[bgfinal][fgfinal]overlay=(W-w)/2:(H-h)/2,fps=30,setsar=1[v]")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}",
         "-t", f"{dur + 0.2:.3f}", "-i", str(inp), "-filter_complex", f, "-map", "[v]",
         "-t", f"{dur:.3f}", "-r", "30", "-an", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "19", "-pix_fmt", "yuv420p", str(out)])


def cmd_build(args: argparse.Namespace) -> None:
    root = project_dir(args.project)
    cues = read_json(root / "06_字幕" / "blind_cues.json")["cues"]
    plan = read_json(root / "07_成片" / "scene_plan.json")
    pool = read_json(Path(args.pool))
    sources = {x["id"]: x for x in pool.get("sources", [])}
    segdir = root / "07_成片" / "segments"
    ovdir = root / "07_成片" / "overlays"
    sdir = root / "07_成片" / "subtitled"
    for d in (segdir, ovdir, sdir):
        d.mkdir(parents=True, exist_ok=True)
        for f in d.glob("*.mp4" if d != ovdir else "*.png"): f.unlink()
    watermark_text = None
    if getattr(args, "watermark", False):
        if not args.watermark_text:
            die("启用水印前必须询问用户，并提供 --watermark-text <用户水印文本>")
        consent_path = Path(args.watermark_consent_file).expanduser().resolve() if args.watermark_consent_file else watermark_consent_path(root)
        consent_path.parent.mkdir(parents=True, exist_ok=True)
        save_watermark_consent(root, args.watermark_text)
        watermark_text = args.watermark_text
        consent_path_relative = consent_path.relative_to(root)
        write_md(root / ".amlei-skill" / "gossip-video" / "watermark.md", f"""# 防盗水印设置\n\n- 水印文本：`{watermark_text}`\n- 位置：右上角\n- 启用时间：UTC\n- 来源：用户在构建前明确提供\n""")
    else:
        consent_path_relative = None
    for i, (cue, p) in enumerate(zip(cues, plan), 1):
        dur = cue["end"] - cue["start"]
        seg = segdir / f"{i:04d}.mp4"
        if p["type"] == "cover":
            build_image(seg, dur, Path(p["path"]).expanduser().resolve(), args.bg_alpha)
        elif p["type"] == "card":
            build_image(seg, dur, Path(p["path"]).expanduser().resolve(), args.bg_alpha)
        elif p["type"] == "source":
            src = sources[p["source_id"]]
            path = Path(src["file"]).expanduser().resolve()
            crop = tuple(src.get("crop", [1138, 640, 391, 90]))
            build_source(seg, dur, path, p["start"], crop)
        else:
            die(f"未知 scene type：{p.get('type')}")
        opng = ovdir / f"{i:04d}.png"
        make_overlay(opng, cue, watermark_text)
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(seg), "-i", str(opng),
             "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto[v]", "-map", "[v]", "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
             str(sdir / f"{i:04d}.mp4")])
    lst = root / "07_成片" / "concat.txt"
    with lst.open("w", encoding="utf-8") as f:
        for i in range(1, len(cues) + 1):
            f.write(f"file '{(sdir / f'{i:04d}.mp4').as_posix()}'\n")
    visual = root / "07_成片" / "visual_subtitled.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(visual)])
    consent_md = root / "08_QC" / "水印授权.md"
    write_md(consent_md, f"""# 水印授权\n\n- 启用：{bool(watermark_text)}\n- 文本：`{watermark_text or "未启用"}`\n- 位置：右上角\n- 授权记录：`{consent_path_relative or "未创建"}`\n- 说明：仅在用户明确确认后启用。\n""")
    print(visual)
    print(consent_md)


def cmd_package(args: argparse.Namespace) -> None:
    root = project_dir(args.project)
    visual = root / "07_成片" / "visual_subtitled.mp4"
    voice = Path(args.audio).expanduser().resolve()
    final = root / "07_成片" / args.final_name
    preview = root / "07_成片" / args.preview_name
    if args.speed and args.speed != 1.0:
        tmp = root / "07_成片" / "final_voice_temp.m4a"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(voice),
             "-af", f"atempo={args.speed},loudnorm=I=-16:TP=-1.5:LRA=11",
             "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(tmp)])
        voice = tmp
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(visual), "-i", str(voice),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(final)])
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(final),
         "-vf", "scale=720:1280", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
         "-pix_fmt", "yuv420p", "-c:a", "copy", str(preview)])
    info = ffprobe_json(final)
    qc = root / "08_QC" / "QC报告.md"
    qc.write_text(qc.read_text(encoding="utf-8") + f"\n\n## 输出\n\n```json\n{json.dumps(info, ensure_ascii=False, indent=2)}\n```\n",
                  encoding="utf-8")
    print(final)
    print(preview)


def cmd_qc(args: argparse.Namespace) -> None:
    root = project_dir(args.project)
    final = Path(args.final).expanduser().resolve()
    info = ffprobe_json(final)
    qdir = root / "08_QC"; qdir.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(final),
         "-vf", "fps=1/10,scale=240:427,tile=5x6", "-frames:v", "1",
         str(qdir / "contact_sheet.jpg")])
    p = run(["ffmpeg", "-hide_banner", "-i", str(final),
             "-vf", "blackdetect=d=0.08:pix_th=0.08", "-an", "-f", "null", "-"])
    blacks = [x for x in p.stderr.splitlines() if "blackdetect" in x]
    cues = read_json(root / "06_字幕" / "blind_cues.json")["cues"]
    overlaps = [(a["id"], b["id"]) for a, b in zip(cues, cues[1:]) if a["end"] > b["start"]]
    report = {"media": info, "black_segments": blacks, "cue_overlaps": overlaps,
              "cue_count": len(cues), "duration": cues[-1]["end"] if cues else 0}
    write_json(qdir / "qc.json", report)
    write_md(qdir / "QC自动报告.md", f"""# QC 自动报告

```json
{json.dumps(report, ensure_ascii=False, indent=2)}
```
""")
    print(qdir / "QC自动报告.md")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Chinese gossip short-video pipeline")
    p.add_argument("--api-key", help="DashScope API key; prefer env or key file")
    p.add_argument("--api-key-file", default=os.environ.get("QWEN_API_KEY_FILE", ".secrets/QWEN_API_KEY"))
    sub = p.add_subparsers(dest="command", required=True)

    q = sub.add_parser("init", help="create project folders and md templates")
    q.add_argument("--slug", required=True)
    q.add_argument("--out", required=True)
    q.add_argument("--title", default="")
    q.add_argument("--force", action="store_true")
    q.add_argument("--tts-model", default=DEFAULT_TTS_MODEL)
    q.add_argument("--asr-model", default=DEFAULT_ASR_MODEL)
    q.set_defaults(func=cmd_init)

    q = sub.add_parser("narration", help="parse 旁白稿.md into narration.json")
    q.add_argument("--project", required=True)
    q.add_argument("--chunk-chars", type=int, default=420)
    q.add_argument("--tts-model", default=DEFAULT_TTS_MODEL)
    q.add_argument("--asr-model", default=DEFAULT_ASR_MODEL)
    q.set_defaults(func=cmd_narration)

    q = sub.add_parser("tts", help="online macro-chunk TTS")
    q.add_argument("--project", required=True)
    q.add_argument("--model", default=DEFAULT_TTS_MODEL)
    q.add_argument("--voice", default=DEFAULT_VOICE)
    q.add_argument("--chunk-chars", type=int, default=420)
    q.add_argument("--sample-rate", type=int, default=24000)
    q.add_argument("--retries", type=int, default=3)
    q.add_argument("--retry-wait", type=float, default=3.0)
    q.add_argument("--timeout", type=float, default=180)
    q.add_argument("--download-timeout", type=float, default=180)
    q.set_defaults(func=cmd_tts)

    q = sub.add_parser("asr", help="online blind file-transcription ASR")
    q.add_argument("--project", required=True)
    q.add_argument("--model", default=DEFAULT_ASR_MODEL)
    q.add_argument("--language", nargs="+", default=["zh"])
    q.add_argument("--audio-url", action="append", help="public audio URL; overrides TTS manifest")
    q.add_argument("--speed", type=float, default=1.0, help="playback speed used for final audio")
    q.add_argument("--polls", type=int, default=240)
    q.add_argument("--poll-wait", type=float, default=2.0)
    q.set_defaults(func=cmd_asr)

    q = sub.add_parser("cues", help="build blind cues from ASR")
    q.add_argument("--project", required=True)
    q.add_argument("--model", default=DEFAULT_ASR_MODEL)
    q.add_argument("--lead", type=float, default=0.10)
    q.add_argument("--tail", type=float, default=0.24)
    q.add_argument("--line-chars", type=int, default=16)
    q.add_argument("--min-group-chars", type=int, default=18)
    q.add_argument("--max-group-chars", type=int, default=46)
    q.set_defaults(func=cmd_cues)

    q = sub.add_parser("plan", help="assign unique clean scenes to cues")
    q.add_argument("--project", required=True)
    q.add_argument("--pool", required=True)
    q.add_argument("--cover", required=True)
    q.set_defaults(func=cmd_plan)

    q = sub.add_parser("build", help="build 9:16 subtitled visual track")
    q.add_argument("--project", required=True)
    q.add_argument("--pool", required=True)
    q.add_argument("--watermark", action="store_true", help="enable watermark; pass only after the user confirms")
    q.add_argument("--watermark-text")
    q.add_argument("--watermark-consent-file")
    q.add_argument("--bg-alpha", type=float, default=0.7,
                   help="blurred background opacity; 0.7 means 30%% transparent")
    q.set_defaults(func=cmd_build)

    q = sub.add_parser("package", help="mux final voice and make preview")
    q.add_argument("--project", required=True)
    q.add_argument("--audio", required=True)
    q.add_argument("--speed", type=float, default=1.0)
    q.add_argument("--final-name", default="成片_1080x1920.mp4")
    q.add_argument("--preview-name", default="成片_720p预览.mp4")
    q.set_defaults(func=cmd_package)

    q = sub.add_parser("qc", help="probe, blackdetect, contact sheet, cue overlap check")
    q.add_argument("--project", required=True)
    q.add_argument("--final", required=True)
    q.set_defaults(func=cmd_qc)
    return p


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
