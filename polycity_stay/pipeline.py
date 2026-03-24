"""Sequential multi-agent pipeline with shared SQLite memory."""

from __future__ import annotations

import json
from typing import Any

from agents import Runner

from polycity_stay.agents import build_agents
from polycity_stay.json_utils import format_for_downstream, parse_json_loose
from polycity_stay.language import buddy_report_language_block, json_strings_language_note
from polycity_stay.memory import insert_run, log_line
from polycity_stay.ollama_setup import ensure_ollama
from polycity_stay.tools import set_tool_context


async def run_polycity_pipeline(
    school_label: str,
    prefs: dict[str, Any],
) -> dict[str, Any]:
    """
    school_label: "CityU" | "PolyU"
    prefs: structured UI fields
    Returns dict with keys retrieval, analysis, verification, final (or error).
    """
    ensure_ollama()
    set_tool_context(school_label)

    retrieval, analysis, verification, buddy = build_agents()
    prefs_json = json.dumps(prefs, ensure_ascii=False, indent=2)

    run_id: int | None = None
    out1 = out2 = out3 = out4 = ""
    err: str | None = None
    pr1 = pr2 = pr3 = None

    try:
        log_line(None, "info", f"Pipeline start: {school_label}")
        m1 = f"""Campus: {school_label}
User preferences (JSON):
{prefs_json}

Use tools. Output JSON as instructed.
Hotel names: keep as in seed / tools (often English). {json_strings_language_note(prefs)}"""
        r1 = await Runner.run(retrieval, m1)
        out1 = r1.final_output or ""
        pr1 = parse_json_loose(out1)
        log_line(
            None,
            "info",
            f"Retrieval done (json_ok={pr1.ok}" + (f", err={pr1.error}" if not pr1.ok else "") + ")",
        )
        retrieval_for_next = format_for_downstream("retrieval", pr1)

        m2 = f"""User preferences JSON:
{prefs_json}

Retrieval output (normalized when parse succeeded):
{retrieval_for_next}

{json_strings_language_note(prefs)}

Return scoring JSON as instructed."""
        r2 = await Runner.run(analysis, m2)
        out2 = r2.final_output or ""
        pr2 = parse_json_loose(out2)
        log_line(
            None,
            "info",
            f"Analysis done (json_ok={pr2.ok}" + (f", err={pr2.error}" if not pr2.ok else "") + ")",
        )
        analysis_for_next = format_for_downstream("analysis", pr2)

        m3 = f"""Verify this scoring output:
{analysis_for_next}

{json_strings_language_note(prefs)}
"""
        r3 = await Runner.run(verification, m3)
        out3 = r3.final_output or ""
        pr3 = parse_json_loose(out3)
        log_line(
            None,
            "info",
            f"Verification done (json_ok={pr3.ok}" + (f", err={pr3.error}" if not pr3.ok else "") + ")",
        )
        verification_for_next = format_for_downstream("verification", pr3)

        ref_snip = retrieval_for_next[:4000]
        if len(retrieval_for_next) > 4000:
            ref_snip += "\n… [truncated]"

        m4 = f"""Verified JSON + disclaimer context:
{verification_for_next}

Original retrieval for reference (optional):
{ref_snip}

{buddy_report_language_block(prefs)}

Write the fun Markdown report for the student following OUTPUT LANGUAGE above."""
        r4 = await Runner.run(buddy, m4)
        out4 = r4.final_output or ""
        log_line(None, "info", "Buddy done")

    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        log_line(None, "error", err)

    key = "cityu" if "city" in school_label.lower() else "polyu"
    run_id = insert_run(
        key,
        prefs,
        retrieval=out1,
        analysis=out2,
        verification=out3,
        final=out4,
        error=err,
    )
    if run_id is not None:
        log_line(run_id, "info", "Run persisted")

    parse_ok = {
        "retrieval": pr1.ok if pr1 else False,
        "analysis": pr2.ok if pr2 else False,
        "verification": pr3.ok if pr3 else False,
    }

    return {
        "run_id": run_id,
        "retrieval": out1,
        "analysis": out2,
        "verification": out3,
        "final": out4,
        "error": err,
        "parse_ok": parse_ok,
    }
