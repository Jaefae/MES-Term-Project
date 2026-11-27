"""Streamlit entry point for the tomato plant expert-system prototype."""

from __future__ import annotations

import streamlit as st

from engine import infer
from presenter import render_inference, render_media
from questions import collect_facts


st.set_page_config(
    page_title="Tomato Tender",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #263a30;
        --green: #315b43;
        --muted: #718075;
        --line: #e2e8df;
        --paper: #fffefa;
        --tomato: #d96f53;
    }
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(ellipse at 8% 0%, rgba(222, 231, 215, .46), transparent 30rem), #f7f6f1;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1040px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .masthead {
        position: relative;
        overflow: hidden;
        padding: .6rem 0 1.1rem;
        border-bottom: 1px solid var(--line);
        animation: fade-up .55s ease-out both;
    }
    .masthead::before {
        content: "";
        position: absolute;
        top: -2.7rem;
        right: 1rem;
        width: 8rem;
        height: 8rem;
        border: 1px solid rgba(76, 117, 83, .13);
        border-radius: 48% 52% 59% 41%;
        background: radial-gradient(circle at 40% 55%, rgba(221, 231, 213, .44), rgba(221, 231, 213, .06) 68%);
        animation: drift 7s ease-in-out infinite;
        pointer-events: none;
    }
    .eyebrow {
        position: relative;
        z-index: 1;
        color: var(--green);
        font-size: .73rem;
        font-weight: 750;
        letter-spacing: .13em;
        text-transform: uppercase;
    }
    .accent-line {
        position: relative;
        z-index: 1;
        width: 3.4rem;
        height: 3px;
        margin-top: .9rem;
        border-radius: 99px;
        background: var(--tomato);
        animation: grow-line .7s .15s ease-out both;
        transform-origin: left center;
    }
    h1, h2, h3 { color: var(--ink); letter-spacing: -.035em; }
    h1 { margin: .6rem 0 .2rem !important; font-size: clamp(2rem, 4vw, 2.8rem) !important; }
    .intro-copy {
        margin: .55rem 0 1.45rem;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.6;
        animation: fade-up .6s .1s ease-out both;
    }
    .scope-line {
        margin: -.75rem 0 1.25rem;
        color: #78857b;
        font-size: .8rem;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--line) !important;
        border-radius: 17px !important;
        background: var(--paper);
        box-shadow: 0 8px 24px rgba(38, 58, 48, .035);
        transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
    }
    .st-key-evidence-card,
    .st-key-details-card,
    .st-key-symptoms-card,
    .st-key-result-card {
        animation: fade-up .55s ease-out both;
    }
    .st-key-details-card { animation-delay: .08s; }
    .st-key-symptoms-card { animation-delay: .16s; }
    .st-key-result-card { animation-delay: .12s; }
    .st-key-evidence-card:hover,
    .st-key-details-card:hover,
    .st-key-symptoms-card:hover {
        border-color: #cfdbcc;
        box-shadow: 0 12px 28px rgba(38, 58, 48, .065);
        transform: translateY(-1px);
    }
    .section-note {
        margin: -.35rem 0 1rem;
        color: var(--muted);
        font-size: .86rem;
        line-height: 1.5;
    }
    [data-testid="stWidgetLabel"] p {
        color: #354b3e;
        font-size: .86rem;
        font-weight: 630;
    }
    [data-testid="stTextInputRootElement"] input,
    [data-testid="stTextArea"] textarea,
    [data-baseweb="select"] > div {
        border-radius: 10px;
        transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
    }
    [data-testid="stTextInputRootElement"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: #78967d;
        box-shadow: 0 0 0 3px rgba(120, 150, 125, .13);
    }
    [data-testid="stFileUploaderDropzone"] {
        border: 1.5px dashed #c8d4c5;
        border-radius: 13px;
        background: #f9faf7;
        transition: border-color .2s ease, background .2s ease, transform .2s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #89a48b;
        background: #f1f6ef;
        transform: translateY(-1px);
    }
    [data-testid="stSegmentedControl"] button {
        border-radius: 8px;
        font-size: .8rem;
        font-weight: 640;
        transition: color .18s ease, background .18s ease, box-shadow .18s ease;
    }
    [data-testid="stBaseButton-primary"] {
        min-height: 2.9rem;
        border: 0;
        border-radius: 11px;
        color: #fff;
        background: var(--tomato);
        font-size: .95rem;
        font-weight: 700;
        box-shadow: 0 6px 15px rgba(217, 111, 83, .17);
        transition: transform .18s ease, background .18s ease, box-shadow .18s ease;
    }
    [data-testid="stBaseButton-primary"]:hover {
        color: #fff;
        background: #c75d43;
        box-shadow: 0 10px 20px rgba(199, 93, 67, .22);
        transform: translateY(-2px);
    }
    [data-testid="stBaseButton-primary"]:active { transform: translateY(0) scale(.99); }
    [data-testid="stAlert"], [data-testid="stExpander"] { border-radius: 12px; }
    .fine-print { color: #7b877d; font-size: .76rem; line-height: 1.55; }
    @keyframes fade-up {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes drift {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(8px) rotate(5deg); }
    }
    @keyframes grow-line {
        from { transform: scaleX(.15); opacity: .45; }
        to { transform: scaleX(1); opacity: 1; }
    }
    @media (max-width: 720px) {
        [data-testid="stMainBlockContainer"] { padding: 1.25rem 1rem 3rem; }
        .masthead::before { right: -.8rem; width: 6rem; height: 6rem; }
        .intro-copy { max-width: 92%; font-size: .94rem; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: .01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="masthead"><div class="eyebrow">Tomato plant care</div><div class="accent-line"></div></div>',
    unsafe_allow_html=True,
)
st.title("Tomato Tender")
st.markdown(
    '<p class="intro-copy">Describe what you notice, add any useful evidence, and get a clear next step from the tomato-care rules.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="scope-line">10 tomato rules · photo, video, audio, and text · evidence shown with each result</p>',
    unsafe_allow_html=True,
)

with st.container(border=True, key="evidence-card"):
    st.markdown("### Add evidence <span style='color:#78857b;font-size:.8em;font-weight:500'>(optional)</span>", unsafe_allow_html=True)
    st.markdown(
        '<p class="section-note">You can use a photo, short video, spoken note, or continue with text only.</p>',
        unsafe_allow_html=True,
    )
    photo_column, video_column, audio_column = st.columns([1.15, 1, 1])
    with photo_column:
        image_files = st.file_uploader(
            "Photos",
            type=("jpg", "jpeg", "png", "webp"),
            accept_multiple_files=True,
            key="plant_images",
            help="Clear views of the whole plant and affected leaves, stems, or fruit are useful.",
        )
    with video_column:
        video_file = st.file_uploader(
            "Short video",
            type=("mp4", "webm"),
            key="plant_video",
        )
    with audio_column:
        audio_file = st.audio_input(
            "Spoken note",
            key="audio_note",
            help="Record a note, then add its transcript or summary below.",
        )
    st.caption("Review the media yourself and confirm any matching observations in the form.")
    render_media(image_files or (), video_file, audio_file)

with st.form("plant_case", clear_on_submit=False):
    with st.container(border=True, key="details-card"):
        st.markdown("### Plant details")
        st.markdown('<p class="section-note">A little care context helps interpret the symptoms.</p>', unsafe_allow_html=True)
        plant_column, watering_column, sunlight_column = st.columns([1.05, 1, 1])
        with plant_column:
            plant_type = st.selectbox(
                "Plant type",
                ("Tomato", "Other / not sure"),
                help="The current rules cover tomato plants.",
            )
        with watering_column:
            watering = st.text_input("Watering routine", placeholder="e.g. every 2 days")
        with sunlight_column:
            sunlight = st.text_input("Direct sunlight", placeholder="e.g. about 6 hours daily")
        notes = st.text_area(
            "Symptoms or notes",
            placeholder="What changed, and when? Add an audio transcript or video summary here.",
            height=90,
        )

    with st.container(border=True, key="symptoms-card"):
        st.markdown("### Confirm the observations")
        st.markdown(
            '<p class="section-note">Choose Yes, No, or Not sure. Unknown answers stay unknown; the rules will ask for missing details.</p>',
            unsafe_allow_html=True,
        )
        facts = collect_facts(
            has_visual_media=bool(image_files or video_file),
            has_text_or_audio=bool(notes.strip() or audio_file),
        )

    submitted = st.form_submit_button(
        "See my assessment",
        type="primary",
        width="stretch",
    )

if submitted:
    st.divider()
    st.markdown("### Your assessment")
    st.caption(
        f"{plant_type} · Watering: {watering.strip() or 'not provided'} · "
        f"Direct sunlight: {sunlight.strip() or 'not provided'}"
    )
    if notes.strip():
        with st.expander("Read the case notes"):
            st.write(notes.strip())

    if plant_type != "Tomato":
        st.warning("The current rules cover tomato plants, so this case cannot be assessed yet.")
    else:
        with st.container(border=True, key="result-card"):
            render_inference(infer(facts), facts)

st.markdown(
    '<p class="fine-print">Tomato Tender is a class project prototype. Its rules are screening patterns, not a confirmed diagnosis. Media is user-reviewed, and each match shows its supporting observations.</p>',
    unsafe_allow_html=True,
)
