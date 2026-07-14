#!/usr/bin/env python3
"""amlei-resume-gen 的个人能力记忆管理（KV 存储）。

记忆是简历生成的唯一能力来源，**写错不可撤回**——所以：
  · 位置优先项目级 <cwd>/.amlei-skill/resume-gen/memory.json，
    否则用户根目录 ~/.amlei-skill/resume-gen/memory.json。
  · init 不覆盖已有；add/update 写前自动备份 memory.json.bak。
  · 调用 add/update 前，Agent 必须已征得用户同意（本脚本不替你问）。

操作（CLI）：
    memory.py path                                          # 记忆文件路径 / 是否存在
    memory.py init --location project|root                  # 首次创建（不覆盖）
    memory.py time [--key KEY]                              # 最后更新时间（整体或某条目；判过时用）
    memory.py find [--key KEY] [--tag T] [--category hard|soft] [--type ability|project]
    memory.py add  --type ability|project --key KEY --value "..." [--category] [--tags a,b] [--long-term] [--url URL] [--tech a,b] [--role R] [--outcome O]
    memory.py update --type ability|project --key KEY --field <f> --value "..."

退出码：0 正常；1 记忆不存在 / 条目不存在 / 已存在不覆盖 / 参数错。
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime

FILE = "memory.json"


def _paths():
    return {
        "project": os.path.join(os.getcwd(), ".amlei-skill", "resume-gen", FILE),
        "root": os.path.join(os.path.expanduser("~"), ".amlei-skill", "resume-gen", FILE),
    }


def resolve():
    """当前生效的记忆文件路径；都不存在返回 None。优先 project。"""
    p = _paths()
    if os.path.isfile(p["project"]):
        return p["project"]
    if os.path.isfile(p["root"]):
        return p["root"]
    return None


def require():
    p = resolve()
    if not p:
        print("✗ 记忆不存在。先 init --location project|root 创建。")
        sys.exit(1)
    return p


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.isfile(path):
        shutil.copy2(path, path + ".bak")  # 备份上一版（不可撤回 → 留退路）
    data["_meta"]["last_updated"] = datetime.now().isoformat(timespec="seconds")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _empty():
    now = datetime.now().isoformat(timespec="seconds")
    return {"_meta": {"created": now, "last_updated": now},
            "profile": {}, "abilities": {}, "projects": {}}


def _section(data, type_):
    return data["abilities"] if type_ == "ability" else data["projects"]


def cmd_path(args):
    p = resolve()
    print(p if p else "NOT FOUND（用 init --location project|root 创建）")


def cmd_init(args):
    p = _paths()[args.location]
    if os.path.isfile(p):
        print(f"✗ 已存在：{p}（init 不覆盖；改内容用 add/update）")
        sys.exit(1)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(_empty(), f, ensure_ascii=False, indent=2)
    print(f"✓ 已创建记忆：{p}")


def cmd_time(args):
    p = require()
    data = _load(p)
    if args.key:
        for t in ("ability", "project"):
            sec = _section(data, t)
            if args.key in sec:
                print(sec[args.key].get("last_updated", "?"))
                return
        print(f"✗ 条目不存在：{args.key}")
        sys.exit(1)
    print(data["_meta"]["last_updated"])


def cmd_find(args):
    p = require()
    data = _load(p)
    out = []
    types = [args.type] if args.type else ["ability", "project"]
    for t in types:
        sec = _section(data, t)
        for k, v in sec.items():
            if args.key and k != args.key:
                continue
            if args.category and v.get("category") != args.category:
                continue
            if args.tag and args.tag not in (v.get("tags") or []):
                continue
            out.append({"type": t, "key": k, **v})
    print(json.dumps(out, ensure_ascii=False, indent=2) if out else "（无匹配）")


def cmd_add(args):
    p = require()
    data = _load(p)
    sec = _section(data, args.type)
    if args.key in sec:
        print(f"✗ 已存在 {args.type}/{args.key}（改用 update）")
        sys.exit(1)
    now = datetime.now().isoformat(timespec="seconds")
    entry = {"value": args.value,
             "tags": (args.tags.split(",") if args.tags else []),
             "long_term": args.long_term, "last_updated": now}
    if args.type == "ability":
        entry["category"] = args.category or "hard"
    else:
        entry["tech"] = (args.tech.split(",") if args.tech else [])
        if args.url:
            entry["url"] = args.url
        if args.role:
            entry["role"] = args.role
        if args.outcome:
            entry["outcome"] = args.outcome
    sec[args.key] = entry
    _save(p, data)
    print(f"✓ 已新增 {args.type}/{args.key}（写前已备份 memory.json.bak）")


def cmd_update(args):
    p = require()
    data = _load(p)
    sec = _section(data, args.type)
    if args.key not in sec:
        print(f"✗ 条目不存在：{args.type}/{args.key}")
        sys.exit(1)
    entry = sec[args.key]
    field = args.field
    if field in ("tags", "tech"):
        val = args.value.split(",")
    elif field == "long_term":
        val = args.value.lower() in ("true", "1", "yes", "y")
    else:
        val = args.value
    entry[field] = val
    entry["last_updated"] = datetime.now().isoformat(timespec="seconds")
    _save(p, data)
    print(f"✓ 已更新 {args.type}/{args.key}.{field}（写前已备份）")


def main():
    ap = argparse.ArgumentParser(description="个人能力记忆管理（KV）。")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("path"); s.set_defaults(func=cmd_path)

    s = sub.add_parser("init")
    s.add_argument("--location", choices=["project", "root"], required=True)
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("time"); s.add_argument("--key"); s.set_defaults(func=cmd_time)

    s = sub.add_parser("find")
    s.add_argument("--key"); s.add_argument("--tag")
    s.add_argument("--category", choices=["hard", "soft"])
    s.add_argument("--type", choices=["ability", "project"])
    s.set_defaults(func=cmd_find)

    s = sub.add_parser("add")
    s.add_argument("--type", choices=["ability", "project"], required=True)
    s.add_argument("--key", required=True); s.add_argument("--value", required=True)
    s.add_argument("--category", choices=["hard", "soft"])
    s.add_argument("--tags"); s.add_argument("--long-term", action="store_true")
    s.add_argument("--url"); s.add_argument("--tech"); s.add_argument("--role"); s.add_argument("--outcome")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("update")
    s.add_argument("--type", choices=["ability", "project"], required=True)
    s.add_argument("--key", required=True); s.add_argument("--field", required=True)
    s.add_argument("--value", required=True)
    s.set_defaults(func=cmd_update)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
