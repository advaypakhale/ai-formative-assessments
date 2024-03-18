from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# Finally, you need to score the student response based on whether the marking points have been captured. If a marking point has been captured, we denote the score by 1, if not we denote it by 0. For example, if 3 marking points are given, then a score of [1, 0, 1] would indicate that the first marking point was captured, the second was not, while the last marking point was captured.

# class Output(BaseModel):
#     feedback: str = Field(description="feedback on student response")
#     scores: list = Field(description="list of scores for each marking point")


# output_parser = JsonOutputParser(pydantic_object=Output)


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

        marking_points_list = "\n".join(marking_points["Sentence"].to_list())

        return marking_points_list

    def generate_examples(self):
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
            },
            {
                "question": "Why does a parachutist decelerate when he opens his parachute?",
                "marking_points": """
                When the parachute opens, the force due to air resistance increases to become greater than the weight of the parachutist.
                The resultant force acts upwards, and the parachutist decelerates.
                """,
                "student_response": "The parachutist decelerates because he faces air resistance.",
                "feedback": "While your response did explain that there is a force of air resistance experienced, you need to explain that this force of air resistance becomes greater than the weight of the parachutist. As such, the resultant force on the parachutist is upwards, so the parachutist decelerates.",
            },
        ]

        example_prompt = PromptTemplate(
            input_variables=[
                "question",
                "marking_points",
                "student_response",
                "feedback",
            ],
            template="""
            Human:
            question={question},
            marking_points={marking_points},
            student_response={student_response},
            
            AI: {feedback}
            """,
        )

        return (examples, example_prompt)

    def generate_prefix_prompt(self):
        prefix_prompt = """
        System:
        You are a teaching assistant for a class of secondary school students.
        The student will be responding to a short-answer question.
        The teacher of the class has already come up with a set of marking points, given under the "marking_points" header, seperated on each line. These marking points are required to be captured within the student's response for them to score points on the question.
        A student response will be given. Your job, is to give feedback to the student, explaining whether their response has managed to accurately capture the essence of each marking point.
        Your feedback needs to be constructive, suggesting improvements to the response with respect to the marking points.
        
        Examples have been provided. Do not respond to these examples.
        
        Provide feedback based on the latest marking_points and student_response.
        Do not acknowledge that you have recieved any data.
        Only provide feedback as if you are talking to the student directly.
        
        EXAMPLES
        """

        return prefix_prompt

    def generate_suffix_prompt(self):
        suffix_prompt = """
        END OF EXAMPLES
        
        DIRECTLY PROVIDE FEEDBACK FOR THIS RESPONSE TO THE STUDENT:
        marking_points={marking_points},
        student_response={student_response},
        """

        input_variables = [
            "marking_points",
            "student_response",
        ]

        return (suffix_prompt, input_variables)

    def generate_feedback(self):
        examples, example_prompt = self.generate_examples()
        marking_points = self.generate_marking_points()
        prefix_prompt = self.generate_prefix_prompt()
        suffix_prompt, input_variables = self.generate_suffix_prompt()

        prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix=prefix_prompt,
            suffix=suffix_prompt,
            input_variables=input_variables,
        )

        llm = Ollama(model="llama2")

        output_parser = StrOutputParser()

        chain = prompt | llm | output_parser

        llm_response = chain.invoke(
            {
                "marking_points": marking_points,
                "student_response": self.student_response,
            }
        )

        return llm_response
