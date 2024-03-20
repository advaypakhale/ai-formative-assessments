import streamlit as st

st.set_page_config(
    page_title="Markus AI Home",
    page_icon="👋",
)

st.write("# Welcome to Markus AI! 👋")

st.sidebar.success(
    "Answer a question in the answer analysis page for instant feedback!"
)

st.markdown(
    """
    Markus is an AI-powered formative assessment tool that provides real-time feedback for teachers and students.
    
    **👈 Answer a question in the answer analysis page for instant feedback!**
"""
)
