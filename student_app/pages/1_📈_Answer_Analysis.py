import pandas as pd
import streamlit as st
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from pages.helper.llm import FeedbackGenerator
from sqlalchemy import text

st.set_page_config(
    page_title="Answer Analysis",
    page_icon="📈",
)

conn = st.connection("main_db", type="sql", ttl=0)

st.markdown("## Select your question below.")
st.sidebar.header("Answer Analysis")


# Selectbox widget
question = st.selectbox(
    "Select Question",
    [
        "Q" + str(row["QuestionID"]) + ": " + row["Description"]
        for idx, row in conn.query("SELECT * FROM Questions", ttl=0).iterrows()
    ],
    label_visibility="hidden",
)


st.write(f"## {question}")
st.write("## Answer the question below.")

with st.form("answer_form", clear_on_submit=True):
    student_reponse = st.text_input("Enter your answer:")

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write(f"Answer: {student_reponse}")

        feedback_generator = FeedbackGenerator(
            connection=conn, question=question, student_response=student_reponse
        )
        feedback = feedback_generator.generate_feedback()

        st.write(feedback)

        # with conn.session as s:
        #     res = s.execute(
        #         "INSERT INTO Questions (Description) VALUES (:description)",
        #         params=dict(description=question),
        #     )
        #     s.commit()

        #     question_id = res.lastrowid

        #     marking_points = edited_df["Sentence"].to_list()

        #     for point in marking_points:
        #         s.execute(
        #             "INSERT INTO MarkingPoints (QuestionID, Sentence) VALUES (:id, :sentence)",
        #             params=dict(id=question_id, sentence=point),
        #         )
        #     s.commit()

# st.dataframe(
#     conn.query(
#         f"SELECT Sentence FROM MarkingPoints WHERE QuestionID = {question_id}",
#         ttl=0,
#     ),
#     column_config={
#         "Sentence": st.column_config.TextColumn(
#             "Marking Point",
#             width="large",
#         ),
#     },
#     hide_index=True,
# )
