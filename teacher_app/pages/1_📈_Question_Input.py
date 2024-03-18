import pandas as pd
import streamlit as st
from sqlalchemy import text

st.set_page_config(
    page_title="Question Input",
    page_icon="📈",
)


st.markdown("# Input your question below.")
st.sidebar.header("Question Input")

with st.form("question_form", clear_on_submit=True):
    question = st.text_input("Enter the short answer question:")

    df = pd.DataFrame(
        [
            {"Sentence": ""},
        ]
    )

    edited_df = st.data_editor(
        df,
        column_config={
            "Sentence": st.column_config.TextColumn(
                "Marking Point",
                width="large",
                required=True,
                help="Enter marking point here",
            ),
        },
        # disabled=[""],
        hide_index=True,
        num_rows="dynamic",
    )

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Question Submitted Successfully!")

        conn = st.connection("main_db", type="sql", ttl=0)

        with conn.session as s:
            res = s.execute(
                text("INSERT INTO Questions (Description) VALUES (:description)"),
                params=dict(description=question),
            )
            s.commit()

            question_id = res.lastrowid

            marking_points = edited_df["Sentence"].to_list()

            for point in marking_points:
                s.execute(
                    text("INSERT INTO MarkingPoints (QuestionID, Sentence) VALUES (:id, :sentence)"),
                    params=dict(id=question_id, sentence=point),
                )
            s.commit()
