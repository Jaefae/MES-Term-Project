import streamlit as st
from engine import forward_chain, matches
from knowledge_base import load_knowledge


# st.session_state.answers maps question id -> answer, in the order asked.
# None means "Not sure": the question was asked, but the fact stays unknown.

def known_answers() -> dict:
    return {qid: value for qid, value in st.session_state.answers.items() if value is not None}


def next_question(kb: dict) -> dict | None:
    """First question not yet answered whose `if` currently matches."""
    known = known_answers()
    for question in kb["questions"]:
        if question["id"] not in st.session_state.answers and matches(question.get("if", {}), known):
            return question
    return None


def save_answer(qid: str, value):
    st.session_state.answers[qid] = value


def go_back():
    st.session_state.answers.popitem()


def restart():
    st.session_state.answers = {}


def ask(question: dict, fact: dict):
    """Draw one question. Returns (value, ready), where ready means it was answered."""
    qid, label = question["id"], question["question"]
    key = f"q_{qid}"

    if fact["type"] == "mmcq":
        st.markdown(label)
        selected = [c for c in fact["choices"] if st.checkbox(c, key=f"{key}_{c}")]
        return selected, bool(selected)

    if fact["type"] == "bool":
        options = {"Yes": True, "No": False}
        if question.get("unsure"):
            options["Not sure"] = None
    else:
        options = {choice: choice for choice in fact["choices"]}
    selected = st.radio(label, list(options), index=None, key=key)
    return options.get(selected), selected is not None


def show_results(kb: dict, answers: dict):
    known, fired = forward_chain(answers, kb["rules"])
    if not known["suspect"]:
        st.info("No matching cause found with these answers.")
        return
    
    st.subheader("Possible causes")
    for ailment_id in known["suspect"]:
        st.markdown("- " + kb["ailments"][ailment_id]["name"])
    st.subheader("Recommendations")
    for ailment_id in known["suspect"]:
        st.markdown("For " + kb["ailments"][ailment_id]["name"] + ": ")
        for line in kb["ailments"][ailment_id]["advice"]:
            st.markdown("- " + line)

    used = {source for rule in kb["rules"] 
            if rule["id"] in fired 
            for source in rule.get("sources", [])}
    if used:
        st.markdown("**Sources**")
        for source_id in sorted(used):
            source = kb["sources"][source_id]
            st.markdown(f"- [{source['title']}]({source['url']}), {source['publisher']}")


@st.fragment
def questionaire():
    kb = load_knowledge()
    st.session_state.setdefault("answers", {})

    with st.container(border=True):
        st.header("Questionnaire")

        question = next_question(kb)
        if question:
            value, ready = ask(question, kb["facts"][question["id"]])
        else:
            show_results(kb, known_answers())

        started = bool(st.session_state.answers)
        with st.container(horizontal=True):
            st.button("Back", on_click=go_back, disabled=not started, width="stretch")
            st.button("Start over", on_click=restart, disabled=not started, width="stretch")
            if question:
                st.button("Next", on_click=save_answer, args=(question["id"], value),
                          disabled=not ready, type="primary", width="stretch")
