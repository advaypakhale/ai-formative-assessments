import streamlit as st
from sqlalchemy import text

st.set_page_config(
    page_title="Formative Assessments AI",
    page_icon="👋",
)

st.write("# Welcome to Formative Assessments AI! 👋")

st.sidebar.success(
    "Select a question in the question analysis page, or add a new question"
)

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
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
