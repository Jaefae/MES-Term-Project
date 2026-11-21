import streamlit as st
import questions

st.set_page_config(
    page_title="Project name",
    page_icon=":material/psychiatry:",
)

st.title("Tomato Tender! Tomato Doc? Root cause...?")

st.markdown(
    """
    Welcome to [Insert project name here].
    
    Upload an *image* or answer some *questions* to get started.
    """
)

imgContainer = st.container(border=True);

img = imgContainer.file_uploader("Upload an image of your tomato plant", "image/*", on_change="rerun")

if(img):
        imgContainer.image(img)

questions.questionaire()
