"""
Post-process Buddy Markdown for Streamlit: theme-aligned indigo accents.

- Replaces 🎒 with a small inline SVG (emoji colour is OS-controlled; CSS can't reliably tint it).
- Replaces keycap emojis 0️⃣–9️⃣ with styled HTML badges (matches .streamlit primary indigo).
"""

from __future__ import annotations

import re

# Match Streamlit theme in .streamlit/config.toml
ACCENT = "#6366f1"
ACCENT_DEEP = "#4f46e5"

# Simple backpack silhouette (24x24), single path — fills with theme indigo
_BACKPACK_SVG = (
    '<span class="pc-backpack" aria-hidden="true">'
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="1.2em" height="1.2em" '
    'style="vertical-align:-0.2em;display:inline-block">'
    f'<path fill="{ACCENT}" d="M9 2h6a2 2 0 0 1 2 2v1h1a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V8a3 3 0 0 1 3-3h1V4a2 2 0 0 1 2-2zm0 3h6V4H9v1zm-2 3a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1H7zm2 2h6v2H9v-2z"/>'
    "</svg></span>"
)

_STYLES = f"""
<style>
.pc-step-num {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.5em;
  height: 1.5em;
  padding: 0 0.35em;
  margin-right: 0.15em;
  border-radius: 0.35em;
  background: linear-gradient(145deg, {ACCENT}, {ACCENT_DEEP});
  color: #f8fafc !important;
  font-weight: 700;
  font-size: 0.88em;
  font-family: ui-sans-serif, system-ui, sans-serif;
  vertical-align: middle;
  line-height: 1;
  box-shadow: 0 1px 2px rgba(0,0,0,0.25);
}}
.pc-backpack {{
  display: inline-block;
  margin: 0 0.1em;
}}
</style>
"""


def _keycap_to_badge(m: re.Match[str]) -> str:
    digit = m.group(1)
    return f'<span class="pc-step-num">{digit}</span>'


def _normalize_markdown_punctuation(md: str) -> str:
    """Some LLMs emit full-width # / * which Streamlit won't parse as Markdown."""
    if not md:
        return md
    # Fullwidth number sign / asterisk (common with CJK input)
    text = md.replace("\uff03", "#").replace("\uff0a", "*")
    return text


def report_styles_html() -> str:
    """
    CSS for inline SVG / step badges. Call ONCE in its own st.markdown(..., unsafe_allow_html=True).
    Do NOT prepend this to the report body — that breaks Markdown rendering in Streamlit.
    """
    return _STYLES


def enhance_buddy_markdown(md: str) -> str:
    """
    Backpack SVG + keycap badges only. Use with st.markdown(..., unsafe_allow_html=True)
    AFTER a separate call with report_styles_html().
    """
    if not md:
        return md

    text = _normalize_markdown_punctuation(md)
    text = text.replace("\U0001f392", _BACKPACK_SVG)  # 🎒 U+1F392

    text = re.sub(
        r"([0-9])\ufe0f\u20e3",
        _keycap_to_badge,
        text,
    )

    return text
