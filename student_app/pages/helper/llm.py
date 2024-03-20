from langchain_community.chat_models.ollama import ChatOllama
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    FewShotPromptTemplate,
    PromptTemplate,
)
from langchain_core.pydantic_v1 import BaseModel, Field


class FeedbackGenerator:
    def __init__(self, connection, question, student_response) -> None:
        self.connection = connection
        self.student_response = student_response
        self.question = question
        self.question_id = question.split(":")[0][1:]

    def generate_marking_points(self):
        marking_points = self.connection.query(
            f"SELECT Sentence FROM MarkingPoints WHERE QuestionID = {self.question_id}",
            ttl=0,
        )

        marking_points_list = marking_points["Sentence"].to_list()

        return marking_points_list

    def generate_examples(self):
        examples = [
            {
                # "question": "What are the three modes of heat transfer?",
                "marking_point": "A mode of heat transfer is conduction.",
                "student_response": "The modes of heat transfer are conduction and convection.",
                "captured": "Conduction as a mode of heat transfer is captured within your response.",
                # "score": "1",
            },
            {
                # "question": "What are the three modes of heat transfer?",
                "marking_point": "A mode of heat transfer is convection.",
                "student_response": "The modes of heat transfer are conduction and convection.",
                "captured": "Convection as a mode of heat transfer is captured within your response.",
                # "score": "1",
            },
            {
                # "question": "What are the three modes of heat transfer?",
                "marking_point": "A mode of heat transfer is radiation.",
                "student_response": "The modes of heat transfer are conduction and convection.",
                "captured": "You have failed to capture radiation as a mode of heat transfer in your response.",
                # "score": "0",
            },
            {
                # "question": "Why does a parachutist decelerate when he opens his parachute?",
                "marking_point": "When the parachute opens, the force due to air resistance increases to become greater than the weight of the parachutist.",
                "student_response": "The parachutist decelerates because he faces air resistance.",
                "captured": "You have failed to completely capture that the force of air resistance increases to become greater than the weight.",
                # "score": 0,
            },
            {
                # "question": "Why does a parachutist decelerate when he opens his parachute?",
                "marking_point": "When the parachute opens, the force due to air resistance increases to become greater than the weight of the parachutist.",
                "student_response": "The parachutist decelerates because he faces air resistance, that rises to become greater than the weight of the parachute.",
                "captured": "Your answer has captured that the force of air resistance increases to become greater than the weight.",
                # "score": 0,
            },
        ]

        example_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "human",
                    """
                    Marking Point: {marking_point}
                    Student Response: {student_response}
                    """,
                ),
                ("ai", "{captured}"),
            ]
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )

        return few_shot_prompt

    def generate_prefix_prompt(self):
        prefix_prompt = """
        You are a teaching assistant for a class of secondary school students.
        The student will be responding to a short-answer question.
        The teacher of the class has already come up with a marking point, given under the "marking_point" header.
        This marking point is required to be captured within the student's response for them to score a point on the question.
        A student response will be given. Your job is to identify whether the marking point has been accurately and completely captured by the student's response.
        
        You will respond within TWO SENTENCES explaining whether you the marking point has been accurately and completely captured.
        Include the marking point within your response.
        Do not use any external knowledge when responding. Do only a direct comparison between the marking point and the student response.
        
        Examples of sample inputs and outputs have been provided. Do not respond to these examples.
        """

        return prefix_prompt

    def generate_suffix_prompt(self):
        suffix_prompt = """
        Marking Point: {marking_point}
        Student Response: {student_response}
        """

        return suffix_prompt

    def generate_feedback(self):
        examples = self.generate_examples()
        marking_points_list = self.generate_marking_points()
        prefix_prompt = self.generate_prefix_prompt()
        suffix_prompt = self.generate_suffix_prompt()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prefix_prompt),
                examples,
                ("human", suffix_prompt),
            ]
        )

        llm = ChatOllama(model="llama2")

        # class Output(BaseModel):
        #     captured: str = Field(
        #         description="one sentence explanation of whether the marking point was captured"
        #     )
        #     score: int = Field(
        #         description="score 1 if marking point captured, 0 if marking point not captured"
        #     )

        # output_parser = JsonOutputParser(pydantic_object=Output)

        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser

        output = []

        for marking_point in marking_points_list:
            llm_response = chain.invoke(
                {
                    "marking_point": marking_point,
                    "student_response": self.student_response,
                    # "formatting_instructions": output_parser.get_format_instructions(),
                }
            )

            output.append(llm_response)

        return output
