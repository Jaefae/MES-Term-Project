"""Streamlit input controls and case-fact collection."""

from __future__ import annotations

import streamlit as st

from engine import FACT_LABELS, Fact


def collect_facts(
    *,
    has_visual_media: bool,
    has_text_or_audio: bool,
) -> dict[str, Fact]:
    """Ask for explicit observations and normalize them for the rule engine."""

    st.caption(
        "Use Not sure whenever you cannot confirm a symptom. The system will ask for missing facts instead of guessing."
    )

    source_options = ["Direct examination"]
    if has_visual_media:
        source_options.append("Photo/video review")
    if has_text_or_audio:
        source_options.append("Text or user-reviewed audio")

    observation_source = st.selectbox(
        "Source for the symptom observations below",
        source_options,
        key="observation_source",
    )

    answers: dict[str, str] = {}
    leaf_and_fruit = (
        "lower_brown_spots_rings",
        "lower_many_gray_spots",
        "large_greasy_patches",
        "fruit_sunken_spot_bottom",
        "lower_yellow_no_spots",
        "leaves_eaten",
        "dark_droppings",
    )
    plant_and_weather = (
        "wilting",
        "stem_brown_inside",
        "flowers_drop",
        "very_hot_or_cold",
    )
    leaves_column, plant_column = st.columns(2)
    with leaves_column:
        st.markdown("**Leaves, fruit, and pests**")
        for fact_key in leaf_and_fruit:
            answers[fact_key] = st.segmented_control(
                FACT_LABELS[fact_key],
                ("Not sure", "Yes", "No"),
                default="Not sure",
                key=f"answer_{fact_key}",
                width="stretch",
            )
    with plant_column:
        st.markdown("**Whole plant and weather**")
        for fact_key in plant_and_weather:
            answers[fact_key] = st.segmented_control(
                FACT_LABELS[fact_key],
                ("Not sure", "Yes", "No"),
                default="Not sure",
                key=f"answer_{fact_key}",
                width="stretch",
            )

    st.markdown("#### Growing conditions")
    environment_left, environment_right = st.columns(2)
    with environment_left:
        soil_condition = st.selectbox(
            "Current soil moisture",
            ("Not sure", "Dry", "Moist", "Soggy"),
            key="soil_condition",
        )
    with environment_right:
        weather_condition = st.selectbox(
            "Recent weather",
            ("Not sure", "Cool and wet", "Not cool and wet"),
            key="weather_condition",
        )

    facts: dict[str, Fact] = {}
    for key, answer in answers.items():
        value = True if answer == "Yes" else False if answer == "No" else None
        facts[key] = Fact(key=key, value=value, source=observation_source)

    soil_values: dict[str, bool | None] = {
        "soil_dry": soil_condition == "Dry" if soil_condition != "Not sure" else None,
        "soil_moist": soil_condition == "Moist" if soil_condition != "Not sure" else None,
        "soil_soggy": soil_condition == "Soggy" if soil_condition != "Not sure" else None,
    }
    for key, value in soil_values.items():
        facts[key] = Fact(
            key=key,
            value=value,
            source="Soil moisture answer" if value is not None else "Not provided",
        )

    if weather_condition == "Not sure":
        weather_value = None
        weather_source = "Not provided"
    else:
        weather_value = weather_condition == "Cool and wet"
        weather_source = "Recent weather answer"
    facts["cool_wet_weather"] = Fact(
        key="cool_wet_weather",
        value=weather_value,
        source=weather_source,
    )

    return facts
