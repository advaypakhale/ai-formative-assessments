import streamlit as st
from pages.helper.llm import FeedbackGenerator

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

        st.json(feedback)
