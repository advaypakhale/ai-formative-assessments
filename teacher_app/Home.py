import streamlit as st
from sqlalchemy import text

st.set_page_config(
    page_title="Markus AI Home",
    page_icon="👋",
)

st.write("# Welcome to Markus AI! 👋")

st.sidebar.success(
    "Select a question in the question analysis page, or add a new question"
)

st.markdown(
    """
    Markus is an AI-powered formative assessment tool that provides real-time feedback for teachers and students. Try it out by
    Machine Learning and Data Science projects.
    **👈 Select a question in the question analysis page, or add a new question!**
"""
)

creation_query = [
    "CREATE TABLE IF NOT EXISTS Questions (QuestionID INTEGER PRIMARY KEY, Description TEXT);",
    "CREATE TABLE IF NOT EXISTS MarkingPoints (MarkingPointID INTEGER PRIMARY KEY, QuestionID INTEGER, Sentence TEXT, FOREIGN KEY(QuestionID) REFERENCES Questions(QuestionID));",
    "CREATE TABLE IF NOT EXISTS MarkingPoints (MarkingPointID INTEGER PRIMARY KEY, QuestionID INTEGER, Sentence TEXT, FOREIGN KEY(QuestionID) REFERENCES Questions(QuestionID));",
    "CREATE TABLE IF NOT EXISTS Students (StudentID INTEGER PRIMARY KEY, Name TEXT);",
    "CREATE TABLE IF NOT EXISTS Answers (AnswerID INTEGER PRIMARY KEY, QuestionID INTEGER, StudentID INTEGER, AnswerText TEXT, FOREIGN KEY(QuestionID) REFERENCES Questions(QuestionID), FOREIGN KEY(StudentID) REFERENCES Students(StudentID));",
    "CREATE TABLE IF NOT EXISTS AnswerMarkingPoints (AnswerMarkingPointID INTEGER PRIMARY KEY, AnswerID INTEGER, MarkingPointID INTEGER, Covered INTEGER, FOREIGN KEY(AnswerID) REFERENCES Answers(AnswerID), FOREIGN KEY(MarkingPointID) REFERENCES MarkingPoints(MarkingPointID));",
]

conn = st.connection("main_db", type="sql")

with conn.session as s:
    for q in creation_query:
        s.execute(text(q))
    s.commit()
