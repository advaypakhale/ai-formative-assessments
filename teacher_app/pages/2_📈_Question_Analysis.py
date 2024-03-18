import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Question Analysis",
    page_icon="📈",
)

conn = st.connection("main_db", type="sql", ttl=0)
# st.session_state["questions"] = conn.query("SELECT * FROM Questions", ttl=0)

st.markdown("# Select your question below.")
st.sidebar.header("Question Analysis")

questions = conn.query("SELECT * FROM Questions", ttl=0)

# Selectbox widget
question = st.selectbox(
    "Select Question",
    [
        "Q" + str(row["QuestionID"]) + ": " + row["Description"]
        for idx, row in questions.iterrows()
    ],
    label_visibility="hidden",
)

marking_points_tab, student_performance_tab = st.tabs(
    ["Marking Points", "Student Performance"]
)

with marking_points_tab:

    question_id = question.split(":")[0][1:]

    st.write(f"## {question}")
    st.write("## Marking Points")

    st.dataframe(
        conn.query(
            f"SELECT Sentence FROM MarkingPoints WHERE QuestionID = {question_id}",
            ttl=0,
        ),
        column_config={
            "Sentence": st.column_config.TextColumn(
                "Marking Point",
                width="large",
            ),
        },
        hide_index=True,
    )


with student_performance_tab:
    pass
