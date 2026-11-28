from pathlib import Path
import yaml

KB_PATH = Path(__file__).parent / "knowledge.yaml"

def load_knowledge(path: Path = KB_PATH) -> dict:
    kb = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate(kb)
    return kb

def check_condition(fact_id: str, value, facts: dict, where: str) -> None:
    """Raise ValueError if `fact_id: value` isn't allowed by the fact definitions."""
    if fact_id not in facts:
        raise ValueError(f"{where} refers to invalid fact '{fact_id}'.")

    fact = facts[fact_id]
    if fact["type"] in ("mcq", "mmcq"):
        if value not in fact["choices"]:
            raise ValueError(f"{where}: '{value}' is not a choice of '{fact_id}'.")
    elif fact["type"] == "bool":
        if not isinstance(value, bool):
            raise ValueError(f"{where}: '{fact_id}' needs true or false, got '{value}'.")

def validate(kb: dict) -> None:
    """Raise ValueError if knowledge base has invalid structure"""
    for question in kb["questions"]:
        qid = question["id"]
        if qid not in kb["facts"]:
            raise ValueError(f"Question '{qid}' has no matching fact.")

        for fact_id, value in question.get("if", {}).items():
            check_condition(fact_id, value, kb["facts"], f"Question '{qid}'")

    for rule in kb["rules"]:
        where = f"Rule '{rule['id']}'"

        for fact_id, value in rule["if"].items():
            check_condition(fact_id, value, kb["facts"], where)

        for key, value in rule["then"].items():
            if key == "suspect":
                if value not in kb["ailments"]:
                    raise ValueError(f"{where} suspects unknown ailment '{value}'.")
            else:
                check_condition(key, value, kb["facts"], where)

        for source_id in rule.get("sources", []):
            if source_id not in kb["sources"]:
                raise ValueError(f"{where} cites unknown source '{source_id}'.")
