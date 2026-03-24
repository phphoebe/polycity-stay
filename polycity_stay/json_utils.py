"""Loose JSON extraction from LLM text (fences, chatter, minor syntax issues)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


def _strip_markdown_fences(text: str) -> str:
    t = text.strip()
    if not t.startswith("```"):
        return t
    t = re.sub(r"^```[a-zA-Z0-9]*\s*\n", "", t, count=1)
    t = re.sub(r"\n```\s*$", "", t, count=1)
    return t.strip()


def _first_balanced(s: str, open_ch: str) -> str | None:
    """Extract first top-level JSON object or array, respecting strings."""
    close = "}" if open_ch == "{" else "]"
    start = s.find(open_ch)
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    i = start
    while i < len(s):
        c = s[i]
        if in_string:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
        else:
            if c == '"':
                in_string = True
            elif c == open_ch:
                depth += 1
            elif c == close:
                depth -= 1
                if depth == 0:
                    return s[start : i + 1]
        i += 1
    return None


def _candidate_snippets(text: str) -> list[str]:
    raw = text or ""
    out: list[str] = []
    seen: set[str] = set()

    def add(s: str) -> None:
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            out.append(s)

    add(raw)
    add(_strip_markdown_fences(raw))
    stripped = _strip_markdown_fences(raw)
    for ch in ("{", "["):
        bal = _first_balanced(stripped, ch)
        if bal:
            add(bal)
    return out


@dataclass(frozen=True)
class JsonLooseResult:
    ok: bool
    value: Any
    raw: str
    error: str | None = None


def parse_json_loose(text: str) -> JsonLooseResult:
    """
    Try to parse one JSON value from model output.
    On failure, ok=False and value=None; raw preserved for downstream fallback.
    """
    raw = text or ""
    if not raw.strip():
        return JsonLooseResult(False, None, raw, "empty output")

    last_err: str | None = None
    for cand in _candidate_snippets(raw):
        try:
            return JsonLooseResult(True, json.loads(cand), raw, None)
        except json.JSONDecodeError as e:
            last_err = str(e)
            continue

    return JsonLooseResult(False, None, raw, last_err or "no JSON found")


def format_for_downstream(stage: str, result: JsonLooseResult) -> str:
    """What the next agent sees: pretty JSON if parse worked, else labelled raw text."""
    if result.ok and result.value is not None:
        return json.dumps(result.value, ensure_ascii=False, indent=2)
    return (
        f"[Note: {stage} output could not be parsed as JSON — using raw text. "
        f"Error: {result.error}]\n\n"
        f"{result.raw}"
    )
