"""End-to-end Streamlit checks for the main case-entry and result paths."""

from __future__ import annotations

import base64
import io
import sys
import wave
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))


def tiny_wav() -> bytes:
    output = io.BytesIO()
    with wave.open(output, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(8000)
        audio.writeframes(b"\x00\x00" * 80)
    return output.getvalue()


def app_text(app: AppTest) -> str:
    rendered: list[str] = []
    for element in app._tree:
        for attribute in ("value", "label"):
            text = getattr(element, attribute, None)
            if text is not None:
                rendered.append(str(text))
    return "\n".join(rendered)


class AppFlowTests(unittest.TestCase):
    def make_app(self) -> AppTest:
        app = AppTest.from_file(str(ROOT_DIR / "src" / "app.py")).run()
        self.assertFalse(app.exception)
        return app

    def set_answer(self, app: AppTest, label: str, value: str) -> None:
        answer = next(group for group in app.button_group if group.label == label)
        answer.set_value(value)

    def submit(self, app: AppTest) -> None:
        app.button[0].click().run()
        self.assertFalse(app.exception)

    def test_page_loads_with_all_case_inputs(self) -> None:
        app = self.make_app()

        self.assertEqual(len(app.file_uploader), 2)
        self.assertEqual(len(app.audio_input), 1)
        self.assertEqual(len(app.button_group), 11)
        self.assertEqual([item.label for item in app.selectbox], [
            "Plant type",
            "Source for the symptom observations below",
            "Current soil moisture",
            "Recent weather",
        ])
        self.assertIn("Tomato Tender", app_text(app))

    def test_confirmed_symptom_produces_explained_rule_match(self) -> None:
        app = self.make_app()
        self.set_answer(app, "Lower leaves have brown spots with rings", "Yes")
        app.text_input[0].set_value("Every two days")
        app.text_input[1].set_value("Six hours")
        app.text_area[0].set_value("The spots started on the lower leaves last week.")

        self.submit(app)

        rendered = app_text(app)
        self.assertIn("Possible early blight", rendered)
        self.assertIn("Lower leaves have brown spots with rings", rendered)
        self.assertIn("Remove affected leaves.", rendered)
        self.assertIn("Watering: Every two days", rendered)
        self.assertIn("Direct sunlight: Six hours", rendered)
        self.assertIn("The spots started on the lower leaves last week.", rendered)

    def test_incomplete_case_requests_the_missing_fact(self) -> None:
        app = self.make_app()
        self.set_answer(app, "The plant is wilting", "Yes")

        self.submit(app)

        rendered = app_text(app)
        self.assertIn("No diagnosis rule is fully supported yet", rendered)
        self.assertIn("Possible underwatering", rendered)
        self.assertIn("The soil is dry", rendered)

    def test_soil_moisture_selects_the_overwatering_rule(self) -> None:
        app = self.make_app()
        self.set_answer(app, "The plant is wilting", "Yes")
        app.selectbox[2].select("Soggy")

        self.submit(app)

        rendered = app_text(app)
        self.assertIn("Possible overwatering", rendered)
        self.assertIn("Water less often and allow the soil to drain.", rendered)

    def test_other_plant_type_shows_supported_scope_message(self) -> None:
        app = self.make_app()
        app.selectbox[0].select("Other / not sure")

        self.submit(app)

        self.assertIn("current rules cover tomato plants", app_text(app))
        self.assertNotIn("What the rules found", app_text(app))

    def test_photo_video_and_audio_inputs_render_and_keep_source(self) -> None:
        app = self.make_app()
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScL+AAAAAElFTkSuQmCC"
        )
        app.file_uploader[0].set_value(("leaf.png", png, "image/png"))
        app.file_uploader[1].set_value(("plant.mp4", b"generated video fixture", "video/mp4"))
        app.audio_input[0].set_value(("note.wav", tiny_wav(), "audio/wav"))
        app.run()
        self.assertFalse(app.exception)

        source_options = app.selectbox[1].options
        self.assertIn("Photo/video review", source_options)
        self.assertIn("Text or user-reviewed audio", source_options)
        self.assertTrue(app.get("image"))
        self.assertTrue(app.get("video"))
        self.assertTrue(app.get("audio"))

        app.selectbox[1].select("Photo/video review")
        self.set_answer(app, "Lower leaves have brown spots with rings", "Yes")
        self.submit(app)

        self.assertIn("source: Photo/video review", app_text(app))


if __name__ == "__main__":
    unittest.main()
