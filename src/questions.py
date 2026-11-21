import streamlit as st

# If user uploads an image we add questions, else ask base questiosn.
# Demo quiz, needs more functionality, questions, and responsiveness.
quiz = [
        "How often do you water the tomato plant?", 
        "How much sunlight does the plant receive?"
]
quizUnits = ["Cups/Day", "Hours of direct"]

def answered():
    st.session_state.answers.append(st.session_state.answerInput)
    st.session_state.questionNum += 1
    st.session_state.answerInput = ""

@st.fragment
def questionaire():
    st.session_state.setdefault("questionNum", 0)
    st.session_state.setdefault("answers", [])

    num = st.session_state.questionNum
    quizContainer = st.container(border=True)
    quizContainer.header("Questionaire")
    
    if num >= len(quiz):
        quizContainer.success("Done! Formulating a plan...")
        i = 0;
        while(i < len(quiz)):
            quizContainer.write(quiz[i] + " " + st.session_state.answers[i] + " " + quizUnits[i])
            i += 1;
        return

    input, submit = quizContainer.columns([0.8, 0.2], vertical_alignment="bottom")
    response = input.text_input(quiz[num], placeholder=quizUnits[num], key="answerInput")
    submit.button("Submit", on_click=answered)






