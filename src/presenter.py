"""Presentation helpers for uploaded evidence and inference results."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import streamlit as st

from engine import FACT_LABELS, Fact, InferenceResult, RuleMatch


def render_media(
    images: Sequence[Any],
    video: Any | None,
    audio: Any | None,
) -> None:
    """Preview user-provided media without implying automatic recognition."""

    if not images and video is None and audio is None:
        return

    with st.expander("Preview the evidence you added", expanded=True):
        for image in images:
            st.image(image, caption=image.name, width="stretch")
        if video is not None:
            st.caption(f"Video: {video.name}")
            st.video(video)
        if audio is not None:
            st.caption("Recorded audio note")
            st.audio(audio)


def _render_support(match: RuleMatch, facts: dict[str, Fact]) -> None:
    if match.supporting_facts:
        st.markdown("**Supporting observations**")
        for key in match.supporting_facts:
            fact = facts[key]
            st.markdown(f"- {FACT_LABELS[key]} _(source: {fact.source})_")


def _render_rule(match: RuleMatch, facts: dict[str, Fact]) -> None:
    st.markdown(f"#### {match.rule.diagnosis}")
    st.caption(f"Matched team rule {match.rule.rule_id}; this is a rule-based candidate, not a probability score.")
    _render_support(match, facts)
    st.markdown("**Suggested next steps**")
    for recommendation in match.rule.recommendations:
        st.markdown(f"- {recommendation}")


def render_inference(result: InferenceResult, facts: dict[str, Fact]) -> None:
    """Show complete matches, missing facts, or why the current case is unresolved."""

    st.markdown("### What the rules found")

    if result.matches:
        st.success(
            f"{len(result.matches)} rule{'s' if len(result.matches) != 1 else ''} "
            "matched the observations you confirmed."
        )
        for match in result.matches:
            with st.container(border=True):
                _render_rule(match, facts)
        st.caption(
            "A rule match is a screening suggestion. Similar symptoms can have different causes; "
            "use the observations and next steps as a starting point."
        )
        return

    if result.observed_fact_count == 0:
        st.info(
            "No rule can be evaluated yet. Mark relevant symptoms as Yes or No and report "
            "soil moisture or recent weather when known."
        )
        return

    if result.candidates:
        st.info(
            "No diagnosis rule is fully supported yet. These patterns have some supporting "
            "observations and need the missing facts below."
        )
        for candidate in result.candidates[:3]:
            with st.expander(
                f"Check this pattern: {candidate.rule.diagnosis} "
                f"({len(candidate.missing_facts)} fact(s) still unknown)"
            ):
                _render_support(candidate, facts)
                st.markdown("**Follow-up observations needed**")
                for key in candidate.missing_facts:
                    st.markdown(f"- {FACT_LABELS[key]}")
        st.caption("Update the answers above and run the assessment again.")
        return

    st.warning(
        "The current answers do not complete any rule pattern. Review the observations or "
        "add more detail, then run the assessment again."
    )
    if result.rejected:
        st.markdown("**Closest patterns ruled out by a reported observation**")
        for rejected in result.rejected[:3]:
            conflicts = ", ".join(FACT_LABELS[key] for key in rejected.contradicting_facts)
            st.markdown(f"- {rejected.rule.diagnosis}: reported evidence conflicts on {conflicts}.")
