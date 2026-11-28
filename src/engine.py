import knowledge_base

kb = knowledge_base.load_knowledge()

def matches(conditions: dict, facts: dict) -> bool:
    for cond, val in conditions.items():
        if cond not in facts:
            return False
        
        known = facts[cond]
        if isinstance(known, list):
            if val not in known:
                return False

        elif known != val:
            return False
    return True
# Returns (known, rule ids used)
def forward_chain(facts: dict, rules: list)-> tuple [dict, list[str]]:
    known = dict(facts)
    known["suspect"] = []
    fired = []

    changed = True
    while changed:
        changed = False
        for rule in rules:
            if rule["id"] in fired or not matches(rule["if"], known):
                continue

            for key, value in rule["then"].items():
                if key != "suspect":
                    known[key] = value
                elif value not in known["suspect"]:
                    known["suspect"].append(value)

            fired.append(rule["id"])
            changed = True

    return known, fired
