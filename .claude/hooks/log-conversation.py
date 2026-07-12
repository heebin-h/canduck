#!/usr/bin/env python3
"""
Log user prompts and Claude responses to docs/logs/session-YYYY-MM-DD.md.

Scope: canduck project directory only (double-guarded: settings.json lives in
.claude/, and this script also checks cwd prefix).

Invocation: registered as both UserPromptSubmit and Stop hooks in
.claude/settings.json. Reads hook JSON from stdin.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

CANDUCK_ROOT = "/Users/heebiny/canduck"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    cwd = data.get("cwd") or os.getcwd()
    if not cwd.startswith(CANDUCK_ROOT):
        sys.exit(0)

    event = data.get("hook_event_name", "")
    if event == "Stop" and data.get("stop_hook_active"):
        sys.exit(0)

    logs_dir = Path(CANDUCK_ROOT) / "docs" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"session-{today}.md"
    if not log_file.exists():
        log_file.write_text(f"# Session Log — {today}\n\n")

    ts = datetime.now().strftime("%H:%M:%S")
    sid = (data.get("session_id") or "unknown")[:8]

    if event == "UserPromptSubmit":
        prompt = (data.get("prompt") or "").rstrip()
        if not prompt:
            sys.exit(0)
        entry = (
            f"\n---\n\n"
            f"## [{ts}] heebin → Claude  `session:{sid}`\n\n"
            f"{prompt}\n"
        )
        with log_file.open("a", encoding="utf-8") as f:
            f.write(entry)
        sys.exit(0)

    if event == "Stop":
        transcript_path = data.get("transcript_path")
        if not transcript_path or not os.path.exists(transcript_path):
            sys.exit(0)

        last_blocks: list[str] = []
        try:
            with open(transcript_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry_obj = json.loads(line)
                    except Exception:
                        continue
                    if entry_obj.get("type") != "assistant":
                        continue
                    msg = entry_obj.get("message", {})
                    content = msg.get("content")
                    if not isinstance(content, list):
                        continue
                    last_blocks = []
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        btype = block.get("type")
                        if btype == "text":
                            text = (block.get("text") or "").rstrip()
                            if text:
                                last_blocks.append(text)
                        elif btype == "tool_use":
                            name = block.get("name", "?")
                            tool_input = block.get("input", {})
                            preview = ""
                            if isinstance(tool_input, dict):
                                # Capture key fields without dumping full payloads
                                for key in ("file_path", "command", "subject", "skill", "description"):
                                    if key in tool_input:
                                        val = str(tool_input[key])
                                        if len(val) > 200:
                                            val = val[:200] + "…"
                                        preview = f" {key}={val!r}"
                                        break
                            last_blocks.append(f"`[tool_use: {name}{preview}]`")
                        elif btype == "thinking":
                            continue
        except Exception:
            sys.exit(0)

        text = "\n\n".join(b for b in last_blocks if b).strip()
        if not text:
            sys.exit(0)

        entry = (
            f"\n## [{ts}] Claude → heebin  `session:{sid}`\n\n"
            f"{text}\n"
        )
        with log_file.open("a", encoding="utf-8") as f:
            f.write(entry)
        sys.exit(0)


if __name__ == "__main__":
    main()
