# Tomato Tender

A multimedia, rule-based expert-system prototype for helping home gardeners investigate tomato plant problems.

## Run the app

**Requirements:** Python 3.13 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/).

From the repository root:

```bash
uv run --python 3.13 streamlit run src/app.py
```

On first run, `uv` creates a local environment and installs the dependencies from `pyproject.toml` and `uv.lock`. Streamlit prints the local URL, usually [http://localhost:8501](http://localhost:8501).

## What the prototype does

1. Accepts photos, a short video, a spoken note, and text describing symptoms and plant care.
2. Lets the user confirm whether each symptom and growing condition is present, absent, or unknown.
3. Combines those source-labeled facts and matches them against ten tomato rules.
4. Shows matched rules, supporting observations, recommended next steps, or missing facts to clarify.

The rule base covers candidate patterns for early blight, Septoria leaf spot, late blight, Fusarium wilt, blossom-end rot, nitrogen deficiency, under- and overwatering, hornworm damage, and temperature stress.

## Code layout

- `src/app.py` connects the multimedia inputs, questionnaire, inference engine, and results page.
- `src/questions.py` collects structured observations and preserves whether each answer was reported as Yes, No, or unknown, along with its source.
- `src/engine.py` stores the rules and performs deterministic matching. It does not invent confidence percentages.
- `src/presenter.py` renders media previews, evidence, rule matches, follow-up facts, and recommendations.

## Current scope and limitations

- The rule base is limited to tomato plants; other plant types are not assessed.
- Photos and videos are shown to the user for review. The app does not automatically detect visual symptoms.
- Audio can be recorded and played back. Users enter a transcript or summary themselves; the app does not run speech recognition.
- Free-text notes remain case context. Users must confirm structured facts before the rules use them.
- The ten rules are the team's initial candidate rules. They are a screening aid and do not replace an expert diagnosis.
