"""Rule base and deterministic inference for the tomato health prototype."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


FACT_LABELS: dict[str, str] = {
    "lower_brown_spots_rings": "Lower leaves have brown spots with rings",
    "lower_many_gray_spots": "Lower leaves have many small spots with gray centers",
    "large_greasy_patches": "Leaves have large, greasy-looking patches",
    "wilting": "The plant is wilting",
    "stem_brown_inside": "The stem is brown inside",
    "fruit_sunken_spot_bottom": "Fruit has a dark, sunken spot on the bottom",
    "lower_yellow_no_spots": "Lower leaves are evenly yellow with no spots",
    "leaves_eaten": "Leaves have been eaten",
    "dark_droppings": "Dark droppings are visible on the plant",
    "flowers_drop": "Flowers are dropping",
    "very_hot_or_cold": "The plant has experienced very hot or cold temperatures",
    "soil_dry": "The soil is dry",
    "soil_moist": "The soil is moist",
    "soil_soggy": "The soil is soggy",
    "cool_wet_weather": "The weather has been cool and wet",
}


OBSERVATION_FACT_KEYS: tuple[str, ...] = (
    "lower_brown_spots_rings",
    "lower_many_gray_spots",
    "large_greasy_patches",
    "wilting",
    "stem_brown_inside",
    "fruit_sunken_spot_bottom",
    "lower_yellow_no_spots",
    "leaves_eaten",
    "dark_droppings",
    "flowers_drop",
    "very_hot_or_cold",
)


@dataclass(frozen=True)
class Fact:
    """A single yes/no/unknown observation and where it came from."""

    key: str
    value: bool | None
    source: str

    @property
    def label(self) -> str:
        return FACT_LABELS[self.key]


@dataclass(frozen=True)
class Rule:
    """An IF-all-conditions-are-true rule and its user-facing advice."""

    rule_id: str
    diagnosis: str
    conditions: tuple[str, ...]
    recommendations: tuple[str, ...]


@dataclass(frozen=True)
class RuleMatch:
    rule: Rule
    supporting_facts: tuple[str, ...]
    missing_facts: tuple[str, ...]
    contradicting_facts: tuple[str, ...]


@dataclass(frozen=True)
class InferenceResult:
    matches: tuple[RuleMatch, ...]
    candidates: tuple[RuleMatch, ...]
    rejected: tuple[RuleMatch, ...]
    observed_fact_count: int


RULES: tuple[Rule, ...] = (
    Rule(
        "R1",
        "Possible early blight",
        ("lower_brown_spots_rings",),
        (
            "Remove affected leaves.",
            "Water at the soil base and avoid wetting foliage.",
        ),
    ),
    Rule(
        "R2",
        "Possible Septoria leaf spot",
        ("lower_many_gray_spots",),
        (
            "Remove affected leaves.",
            "Improve airflow around the plant.",
        ),
    ),
    Rule(
        "R3",
        "Possible late blight",
        ("large_greasy_patches", "cool_wet_weather"),
        (
            "The proposed rule recommends removing the affected plant.",
            "Seek local extension guidance promptly because this pattern can spread quickly.",
        ),
    ),
    Rule(
        "R4",
        "Possible Fusarium wilt",
        ("wilting", "soil_moist", "stem_brown_inside"),
        (
            "The proposed rule recommends removing the affected plant.",
            "Rotate the location used for future tomato plants.",
        ),
    ),
    Rule(
        "R5",
        "Possible blossom-end rot",
        ("fruit_sunken_spot_bottom",),
        (
            "Keep watering consistent.",
            "Check that soil moisture stays even as fruit develops.",
        ),
    ),
    Rule(
        "R6",
        "Possible nitrogen deficiency",
        ("lower_yellow_no_spots",),
        (
            "Review the plant's nutrient needs.",
            "Fertilize only as appropriate for the soil and product directions.",
        ),
    ),
    Rule(
        "R7",
        "Possible underwatering",
        ("wilting", "soil_dry"),
        ("Water deeply, then check soil moisture before watering again.",),
    ),
    Rule(
        "R8",
        "Possible overwatering",
        ("wilting", "soil_soggy"),
        (
            "Water less often and allow the soil to drain.",
            "Check that the container or planting area has adequate drainage.",
        ),
    ),
    Rule(
        "R9",
        "Possible hornworm damage",
        ("leaves_eaten", "dark_droppings"),
        ("Inspect the plant and handpick visible hornworms.",),
    ),
    Rule(
        "R10",
        "Possible temperature stress",
        ("flowers_drop", "very_hot_or_cold"),
        (
            "Wait for temperatures to improve.",
            "Provide shade during excessive heat when practical.",
        ),
    ),
)


def infer(facts: Mapping[str, Fact]) -> InferenceResult:
    """Match confirmed facts against rules without inventing probabilities.

    A complete match requires every condition to be explicitly true. A false
    condition rejects that rule; an unknown condition leaves it as a candidate
    only when at least one other condition supports the pattern.
    """

    matches: list[RuleMatch] = []
    candidates: list[RuleMatch] = []
    rejected: list[RuleMatch] = []

    for rule in RULES:
        supporting: list[str] = []
        missing: list[str] = []
        contradicting: list[str] = []

        for key in rule.conditions:
            fact = facts.get(key)
            if fact is None or fact.value is None:
                missing.append(key)
            elif fact.value:
                supporting.append(key)
            else:
                contradicting.append(key)

        result = RuleMatch(
            rule=rule,
            supporting_facts=tuple(supporting),
            missing_facts=tuple(missing),
            contradicting_facts=tuple(contradicting),
        )

        if not missing and not contradicting:
            matches.append(result)
        elif not contradicting and supporting:
            candidates.append(result)
        elif supporting or contradicting:
            rejected.append(result)

    candidates.sort(
        key=lambda result: (
            len(result.missing_facts),
            -len(result.supporting_facts),
            -len(result.rule.conditions),
            result.rule.rule_id,
        )
    )
    rejected.sort(
        key=lambda result: (
            -len(result.supporting_facts),
            len(result.contradicting_facts),
            result.rule.rule_id,
        )
    )

    return InferenceResult(
        matches=tuple(matches),
        candidates=tuple(candidates),
        rejected=tuple(rejected),
        observed_fact_count=sum(fact.value is not None for fact in facts.values()),
    )
