import os
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import SequentialChain
from redis import Redis
from langchain.cache import RedisCache
import langchain
import streamlit as st

os.environ['OPENAI_API_KEY'] = st.secrets["openai_api_key"]
langchain.debug = st.secrets["langchain"]["debug"]
langchain.llm_cache = RedisCache(redis_=Redis(host=st.secrets["redis"]["host"],
                                              port=st.secrets["redis"]["port"], db=0))


def question_to_words_chain(llm):
    # Prompt
    template = """
    You will be given a question.
    Your goal is to transform the question to 3 words maximum. Remove the question mark.
    {format_instructions}

    <question>
    {question}
    </question>
    words:"""
    format = """
    ```
    words:transformed question
    ...
    ```
    e.g of words:
    ```
    <question>
    What are the intellectual property rights?
    </question>
    words:Intellectual Property Rights
    ```"""
    prompt = PromptTemplate(input_variables=["question"],
                            partial_variables={"format_instructions": format}, template=template)
    return LLMChain(llm=llm, prompt=prompt, output_key="words", verbose=True)


def words_to_emoji(llm):
    # Prompt
    template = """
    You will be given a set of words.
    Your goal is to understand the sequence of words and choose the best emoji to describe it.
    You should only output an emoji.
    {format_instructions}

    <words>
    {words}
    </words>
    emoji:"""
    format = """
    ```
    emoji:emoji best describing the words
    ...
    ```
    e.g of emoji:
    ```
    <words>
    Intellectual Property Rights
    </words>
    emoji:👨‍💼
    ```"""

    prompt = PromptTemplate(input_variables=["words"],
                            partial_variables={"format_instructions": format}, template=template)
    return LLMChain(llm=llm, prompt=prompt, output_key="emoji", verbose=True)


# Define your desired data structure.
class TermsAnswer(BaseModel):
    answer: str = Field(description="Answer of the question")
    excerpts: str = Field(description="Phrase from terms that justify the answer")


def answer_question_chain(llm):
    # Prompt
    template = """
    Your goal is to read a term of use and answer questions about it.
    Additionnaly, provide excerpts of the text that justify your answer.
    {format_instructions}

    <terms>
    {terms}
    </terms>
    <question>
    {question}
    </question>
    output:"""

    # Set up a parser + inject instructions into the prompt template.
    parser = PydanticOutputParser(pydantic_object=TermsAnswer)

    prompt = PromptTemplate(input_variables=["terms", "question"],
                            partial_variables={
                                "format_instructions": parser.get_format_instructions()},
                            template=template)
    return LLMChain(llm=llm, prompt=prompt, output_key="output", verbose=True)


def overall_chain_exec(questions: list, terms: str):
    llm = ChatOpenAI(temperature=0,
                     model_name="gpt-3.5-turbo-16k")
    llm2 = ChatOpenAI(temperature=0,
                      model_name="gpt-3.5-turbo")

    answers = {}

    seq_chain = SequentialChain(
        chains=[question_to_words_chain(llm2), words_to_emoji(llm2), answer_question_chain(llm)],
        input_variables=["terms", "question"],
        output_variables=["words", "emoji", "output"],
        verbose=True)
    for question in questions:
        term_answer = seq_chain({
            "terms": terms,
            "question": question
            }, return_only_outputs=True)

        # Add the answer to the dictionary
        parser = PydanticOutputParser(pydantic_object=TermsAnswer)
        answers[question] = {
            "emoji": term_answer["emoji"],
            "words": term_answer["words"],
            "answer": parser.parse(term_answer["output"]).answer,
            "excerpts": parser.parse(term_answer["output"]).excerpts,
        }
    return answers
