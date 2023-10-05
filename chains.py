from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


def check_question_parser(questions: str) -> list:
    """
    Parse the ouput string of the check question parser and return a list of questions.
    """
    list_questions = []
    for question in questions.split("\n"):
        if question and question != "-":
            list_questions.append(question.strip())
    return list_questions


def check_question_chain(openai_api_key):
    # Instantiate LLM model
    llm = ChatOpenAI(temperature=0,
                     model_name="gpt-3.5-turbo-16k",
                     openai_api_key=openai_api_key)
    # Prompt
    template = """
    You will be given a question. Your goal is to split the question into multiple one.
    In case the question is a single question output it as is.
    You must follow the output format below.
    <format_instructions>
    {format_instructions}
    </format_instructions>

    <question>
    {question}
    </question>
    questions_list:"""

    format = """
    The output is a list of questions.
    ```
    questions_list:
    - question1 ?
    - question2 ?
    ...
    ```
    e.g of questions_list:
    ```
    <question>
    What are the intellectual property rights and content usage policies?
    </question>
    questions_list:
    - What are the intellectual property rights ?
    - What are the content usage policies ?
    ```"""

    prompt = PromptTemplate(input_variables=["questions"],
                            partial_variables={"format_instructions": format}, template=template)
    return LLMChain(llm=llm, prompt=prompt, output_key="questions_list")


def transform_question_parser(emojify_question: str):
    """
    Parse the chain output to a dictionary of questions and emojis.
    The emojify_question format is:
    question1 ? / emoji and transformed question

    It must be parsed to:
    {
        "question1": {
            "emoji": "emoji",
            "transformed_question": "transformed question"
        }
    }
    """
    parsed_questions = {}
    for question in emojify_question.split("\n"):
        if question and question != "-":
            question = question.strip()
            question = question.split("/")
            parsed_questions[question[0].strip()] = {
                "emoji": question[1].strip().split(" ")[0],
                "transformed_question": " ".join(question[1].strip().split(" ")[1:])
            }


def transform_question(openai_api_key):
    """ Emojify a question and simplify it."""
    # Instantiate LLM model
    llm = ChatOpenAI(temperature=0,
                     model_name="gpt-3.5-turbo-16k",
                     openai_api_key=openai_api_key)
    # Prompt
    template = """
    You will be given a question.
    Your goal is to transform the question by adding a corresponding emoji
    and replace the question to 3 words maximum. Remove the question mark.
    Use this following format for the output:
    <format_instructions>
    {format_instructions}
    </format_instructions>
    <question>
    {question}
    </question>
    emojify_question:"""
    format = """
    ```
    emojify_question:question1 ? / emoji and transformed question
    ...
    ```
    e.g of questions_list:
    ```
    <question>
    What are the intellectual property rights?
    </question>
    emojify_question:What are the intellectual property rights? /👨‍💼 Intellectual Property Rights
    ```"""
    prompt = PromptTemplate(input_variables=["question"],
                            partial_variables={"format_instructions": format}, template=template)
    return LLMChain(llm=llm, prompt=prompt, output_key="emojify_question")


def answer_question_chain(openai_api_key):
    # Instantiate LLM model
    llm = ChatOpenAI(temperature=0,
                     model_name="gpt-3.5-turbo-16k",
                     openai_api_key=openai_api_key)
    # Prompt
    template = """
    Your goal is to read a term of use and answer questions about it.
    Additionnaly, provide excerpts of the text that justify your answer.
    Follow the output format below.
    <format_instructions>
    {format_instructions}
    </format_instructions>
    <terms>
    {terms}
    </terms>
    <question>
    {questions}
    </questions>
    output:"""
    format = """
    ```json
    output: {
        "question1": {
            "answer": "answer of question1",
            "excerpts" : "excerpts of question1"
        },
        "question2": {
            "answer": "answer of question2",
            "excerpts" : "excerpts of question2"
        },
        ...
    }
    ```
    e.g of output:
    ```json
    output: {
        "Does the website collect personal information from users?": {
            "answer": "Yes, Instagram collects personal information from its users.",
            "excerpts" : "Providing our Service requires collecting and using your information"
            }
    }
    ```"""

    prompt = PromptTemplate(input_variables=["terms", "questions"],
                            partial_variables={"format_instructions": format}, template=template)
    return LLMChain(llm=llm, prompt=prompt, output_key="output")
