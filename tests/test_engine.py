"""Unit tests for the tomato rule-matching engine."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from engine import FACT_LABELS, RULES, Fact, infer  # noqa: E402


def make_facts(values: dict[str, bool | None] | None = None) -> dict[str, Fact]:
    values = values or {}
    return {
        key: Fact(key=key, value=values.get(key), source="unit test")
        for key in FACT_LABELS
    }


class InferenceTests(unittest.TestCase):
    def test_each_rule_matches_when_all_of_its_conditions_are_true(self) -> None:
        for rule in RULES:
            with self.subTest(rule=rule.rule_id):
                values = {key: False for key in FACT_LABELS}
                values.update({key: True for key in rule.conditions})

                result = infer(make_facts(values))

                self.assertEqual(
                    [match.rule.rule_id for match in result.matches],
                    [rule.rule_id],
                )
                self.assertEqual(result.matches[0].supporting_facts, rule.conditions)

    def test_missing_required_fact_returns_clarification_candidate(self) -> None:
        result = infer(make_facts({"wilting": True}))

        underwatering = next(
            candidate for candidate in result.candidates if candidate.rule.rule_id == "R7"
        )
        self.assertEqual(underwatering.missing_facts, ("soil_dry",))
        self.assertEqual(underwatering.supporting_facts, ("wilting",))
        self.assertEqual(result.matches, ())

    def test_contradicted_fact_rejects_a_candidate_rule(self) -> None:
        result = infer(make_facts({"wilting": True, "soil_dry": False}))

        self.assertNotIn("R7", [match.rule.rule_id for match in result.matches])
        self.assertNotIn("R7", [match.rule.rule_id for match in result.candidates])
        underwatering = next(
            rejected for rejected in result.rejected if rejected.rule.rule_id == "R7"
        )
        self.assertEqual(underwatering.contradicting_facts, ("soil_dry",))

    def test_unknown_facts_do_not_force_a_diagnosis(self) -> None:
        result = infer(make_facts())

        self.assertEqual(result.matches, ())
        self.assertEqual(result.candidates, ())
        self.assertEqual(result.observed_fact_count, 0)

    def test_independent_complete_rules_can_both_match(self) -> None:
        result = infer(
            make_facts(
                {
                    "lower_brown_spots_rings": True,
                    "fruit_sunken_spot_bottom": True,
                }
            )
        )

        self.assertEqual(
            [match.rule.rule_id for match in result.matches],
            ["R1", "R5"],
        )


if __name__ == "__main__":
    unittest.main()
