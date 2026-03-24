"""PolyCity Stay — Streamlit UI (student-friendly vibes)."""

from __future__ import annotations

import asyncio

import streamlit as st

from polycity_stay.memory import init_db, recent_runs
from polycity_stay.pipeline import run_polycity_pipeline
from polycity_stay.report_render import enhance_buddy_markdown, report_styles_html

TAGLINE = "Your Kowloon long-stay hotel sidekick — CityU & PolyU MVP 🏙️"


def main() -> None:
    st.set_page_config(
        page_title="PolyCity Stay",
        page_icon="🏙️",
        layout="wide",
    )

    init_db()

    st.title("PolyCity Stay")
    st.caption(TAGLINE)
    st.markdown(
        """
        Hey! 👋 Moving to HK for your master’s and *not* trying to fight the rental market solo?  
        We’re here to **hunt long-stay hotel vibes** near **CityU** or **PolyU** — with the stuff students actually care about  
        (MTR access when typhoon mood hits 🌀, shower-not-bathtub, desk space for your monitor setup 💻).
        """
    )

    with st.sidebar:
        st.subheader("Setup check ✨")
        st.markdown(
            """
            1. Install & run **[Ollama](https://ollama.com/)**  
            2. Pull the model (in terminal):
            ```
            ollama pull qwen2.5:7b
            ```
            3. `cp .env.example .env` and tweak if needed  
            """
        )
        st.divider()
        st.caption("Demo data = seed JSON + optional live fetch (sites may block bots — that’s normal!)")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        school = st.radio(
            "Which campus are you aiming for? 🎯",
            ("CityU — Hong Kong City University", "PolyU — Hong Kong Polytechnic University"),
            horizontal=False,
        )
        report_lang = st.radio(
            "Report language / 报告语言 📝",
            ("English", "简体中文"),
            horizontal=True,
            help="Final write-up from PolyCity Buddy + matching language in JSON blurbs (nerd mode). Simplified Chinese for mainland-HK students.",
        )

    with col_b:
        st.markdown("##### Your non-negotiables (we gotchu)")
        max_walk = st.slider("Max walk to MTR (minutes) 🚶 — typhoon days are *not* the day for hikes", 3, 25, 10)
        shower_only = st.checkbox("I need a shower stall — **no bathtub** 🚿", value=True)
        desk_monitor = st.checkbox("Desk must handle **laptop + external monitor** 🖥️", value=True)
        c1, c2 = st.columns(2)
        with c1:
            budget_min = st.number_input("Budget min (HKD / month)", min_value=4000, max_value=50000, value=9000, step=500)
        with c2:
            budget_max = st.number_input("Budget max (HKD / month)", min_value=5000, max_value=80000, value=18000, step=500)

    extra = st.text_area(
        "Anything else? (optional — e.g. late-night food, quiet floor, roommate, etc.)",
        placeholder="e.g. I need halal options nearby / I’m noise-sensitive…",
        height=80,
    )

    _lang_map = {"English": "en", "简体中文": "zh-Hans"}

    prefs = {
        "max_walk_minutes_to_mtr": max_walk,
        "shower_stall_only": shower_only,
        "desk_for_external_monitor": desk_monitor,
        "budget_hkd_monthly_min": int(budget_min),
        "budget_hkd_monthly_max": int(budget_max),
        "extra_notes": extra.strip() or None,
        "output_language": _lang_map[report_lang],
    }

    go = st.button("Let’s find my stay already 🎉", type="primary", use_container_width=True)

    if go:
        label = "CityU" if school.startswith("CityU") else "PolyU"
        with st.spinner("Agents are doing their thing… grab milk tea 🧋"):
            result = asyncio.run(run_polycity_pipeline(label, prefs))

        if result.get("error"):
            st.error(
                "Oops — something went sideways 😵‍💫\n\n"
                f"`{result['error']}`\n\n"
                "Usually this means Ollama isn’t running or the model name doesn’t match `.env`. "
                "Peek at the raw stages below if you’re debugging."
            )
        else:
            st.success("We’re done! Here’s your vibe check 👇")
            po = result.get("parse_ok") or {}
            cols = st.columns(3)
            cols[0].caption(f"Retrieval JSON parse: {'✅' if po.get('retrieval') else '⚠️ loose'}")
            cols[1].caption(f"Analysis JSON parse: {'✅' if po.get('analysis') else '⚠️ loose'}")
            cols[2].caption(f"Verification JSON parse: {'✅' if po.get('verification') else '⚠️ loose'}")
            final_md = result.get("final") or "_No final text — check verification stage._"
            # Styles must be a separate markdown call — mixing <style> + body breaks Markdown parsing (esp. 中文).
            st.markdown(report_styles_html(), unsafe_allow_html=True)
            st.markdown(enhance_buddy_markdown(final_md), unsafe_allow_html=True)

        with st.expander("Nerd mode: raw agent outputs 🤓"):
            st.markdown("**Retrieval**")
            st.code(result.get("retrieval") or "—", language="json")
            st.markdown("**Scoring**")
            st.code(result.get("analysis") or "—", language="json")
            st.markdown("**Verification**")
            st.code(result.get("verification") or "—", language="json")

    st.divider()
    st.subheader("Recent runs (local SQLite memory) 📚")
    rows = recent_runs(5)
    if not rows:
        st.info("No runs yet — hit the big button when you’re ready!")
    else:
        for r in rows:
            with st.container():
                st.markdown(f"**#{r['id']}** · `{r['school']}` · {r['created_at']}")
                if r.get("error"):
                    st.caption(f"⚠️ {r['error'][:120]}…")


if __name__ == "__main__":
    main()
