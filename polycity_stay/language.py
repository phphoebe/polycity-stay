"""Output language hints for agent prompts (prefs['output_language'])."""

from __future__ import annotations

from typing import Any

# Stored in prefs from UI: "en" | "zh-Hans"


def json_strings_language_note(prefs: dict[str, Any]) -> str:
    """Instruction for retrieval / analysis / verification human-readable string fields."""
    lang = prefs.get("output_language", "en")
    if lang == "zh-Hans":
        return (
            "For every human-readable string INSIDE the JSON (hotel names may stay as in seed; "
            "for pros, cons, dealbreakers, reasons, summary_one_liner, flags.issue, student_disclaimer): "
            "use Simplified Chinese (简体中文), natural for mainland-HK students. Keep JSON keys in English."
        )
    return "For every human-readable string INSIDE the JSON, use English. Keep JSON keys in English."


def buddy_report_language_block(prefs: dict[str, Any]) -> str:
    """Mandatory language block for the Buddy (final Markdown) step."""
    lang = prefs.get("output_language", "en")
    if lang == "zh-Hans":
        return (
            "OUTPUT LANGUAGE (mandatory): Simplified Chinese (简体中文).\n"
            "Write the ENTIRE Markdown report in Simplified Chinese. "
            "Keep English for international hotel brand names when usual. "
            "Do not write the main report in English.\n\n"
            "VOICE (简体中文): 活泼、像靠谱学长学姐和同学聊天 —— 口语一点，少用公文/主持稿腔（避免「大家好」「欢迎各位」这种）。"
            "可以适度玩梗、轻松吐槽租房痛点；emoji 点缀即可别刷屏。"
            "要像学生真的会转发给室友看的语气。"
        )
    return (
        "OUTPUT LANGUAGE (mandatory): English.\n"
        "Write the ENTIRE Markdown report in English. "
        "You may keep Cantonese particles in quoted speech only if quoting a HK phrase — otherwise stay in English."
    )
