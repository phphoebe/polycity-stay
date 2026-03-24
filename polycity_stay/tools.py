"""Tools for retrieval agent (seed data + optional HTTP fetch)."""

from __future__ import annotations

import json
from typing import Any

import httpx
from bs4 import BeautifulSoup
from agents import function_tool

from polycity_stay.config import HTTP_TIMEOUT_S, MAX_FETCH_CHARS, SEED_PATH

_tool_context: dict[str, str] = {"school": "cityu"}


def set_tool_context(school: str) -> None:
    """Bind campus key: cityu | polyu (lowercase)."""
    key = school.lower().replace(" ", "")
    if "city" in key or key == "cityu":
        _tool_context["school"] = "cityu"
    elif "poly" in key or key == "polyu":
        _tool_context["school"] = "polyu"
    else:
        _tool_context["school"] = "cityu"


@function_tool
def list_seed_hotels_for_campus() -> str:
    """Load curated demo hotel rows for the campus already selected in the app (CityU or PolyU). Returns JSON text."""
    path = SEED_PATH
    if not path.exists():
        return json.dumps({"error": "seed file missing", "hotels": []})
    data = json.loads(path.read_text(encoding="utf-8"))
    key = _tool_context.get("school", "cityu")
    hotels = data.get(key, [])
    return json.dumps(
        {"campus": key, "count": len(hotels), "hotels": hotels},
        ensure_ascii=False,
        indent=2,
    )


@function_tool
def fetch_webpage_text(url: str) -> str:
    """Fetch a public https URL and return plain text (truncated). Use for extra context; may fail on paywalls or bot checks."""
    if not url.startswith("https://"):
        return json.dumps({"ok": False, "error": "only https URLs supported"})
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT_S, follow_redirects=True) as client:
            r = client.get(url, headers={"User-Agent": "PolyCityStay/0.1 (student project)"})
        if r.status_code >= 400:
            return json.dumps(
                {"ok": False, "status": r.status_code, "hint": "Site blocked or error — seed data still usable."}
            )
        raw = r.text
        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        blob = "\n".join(lines)[:MAX_FETCH_CHARS]
        return json.dumps(
            {"ok": True, "url": url, "chars": len(blob), "text_excerpt": blob},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e), "hint": "Totally normal for some hotel sites — rely on seed + your own checks."})


def tool_list() -> list[Any]:
    return [list_seed_hotels_for_campus, fetch_webpage_text]
