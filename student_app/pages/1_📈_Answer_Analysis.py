import pandas as pd
import streamlit as st
from langchain.llms import Ollama
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
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

question_id = question.split(":")[0][1:]

st.write(f"## {question}")
st.write("## Answer the question below.")

with st.form("answer_form", clear_on_submit=True):
    answer = st.text_input("Enter your answer:")

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write(f"Answer: {answer}")

        marking_points = conn.query(
            f"SELECT Sentence FROM MarkingPoints WHERE QuestionID = {question_id}",
            ttl=0,
        )

        marking_points_list = "\n".join(marking_points["Sentence"].to_list())

        examples = [
            {
                "question": "What are the three modes of heat transfer?",
                "marking_points": """
                The first mode of heat transfer is conduction.
                The second mode of heat transfer is convection.
                The third mode of heat transfer is radiation.
                """,
                "student_response": "The three modes of heat transfer are conduction and convection.",
                "feedback": "While your response accurately captured that conduction and convection are indeed modes of heat transfer, you have missed out on radiation as a source of heat transfer.",
                "scores": "[1, 1, 0]",
            },
        ]

        example_prompt = PromptTemplate(
            input_variables=[
                "question",
                "marking_points",
                "student_response",
                "feedback",
                "scores",
            ],
            template="""
            INPUT
            Question: {question}
            Marking Points:
            {marking_points}
            Student Response: {student_response}
            
            OUTPUT
            feedback={feedback},
            scores={scores}
            """,
        )

        prefix_prompt = """
        You are a teaching assistant for a class of secondary school students.
        The student will be responding to a short-answer question.
        The teacher of the class has already come up with a set of marking points, given under the "Marking Points" header, seperated on each line. These marking points are required to be captured within the student's response for them to score points on the question.
        A student response will be given. Your job, is to produce feedback, explaining whether the student's response has managed to accurately capture the essence of each marking point. Your feedback needs to be constructive, suggesting improvements to the student's answer with respect to the marking points.
        Finally, you need to score the student response based on whether the marking points have been captured. If a marking point has been captured, we denote the score by 1, if not we denote it by 0. For example, if 3 marking points are given, then a score of [1, 0, 1] would indicate that the first marking point was captured, the second was not, while the last marking point was captured.
        Examples have been provided below, consisting of your example INPUT and OUTPUT.
        Under OUTPUT, you can see in the example that there are two fields, feedback and scores, which respectively refer to the feedback you provide and the scores you provide.
        You should return the feedback and scores in a JSON format, with "feedback" and "scores" as keys.
        Populate the JSON output yourself, and remove any non-viable or non-feasible options from the json.
        """

        suffix_prompt = """
        Question: {question}
        Marking Points:
        {marking_points}
        Student Response: {student_response}
        """

        prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix=prefix_prompt,
            suffix=suffix_prompt,
            input_variables=["question", "marking_points", "student_response"],
        )

        output_parser = SimpleJsonOutputParser()

        llm = Ollama(model="llama2")

        chain = prompt | llm | output_parser

        llm_response = chain.invoke(
            {
                "question": question,
                "marking_points": marking_points,
                "student_response": answer,
            }
        )

        st.json(llm_response)

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
