import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

st.title("🦜🔗 Langchain Quickstart App")

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"


def generate_response(terms):
    # Instantiate LLM model
    llm = OpenAI(model_name="text-davinci-003", openai_api_key=openai_api_key)
    # Prompt
    template = "As an experienced data scientist and technical writer, generate an outline for a blog about {termsd}."
    prompt = PromptTemplate(input_variables=["terms"], template=template)
    prompt_query = prompt.format(terms=terms)
    # Run LLM model
    response = llm(prompt_query)
    # Print results
    return st.info(response)


with st.form("my_form"):
    text = st.text_area("Enter text:", "What are 3 key advice for learning how to code?")
    submitted = st.form_submit_button("Submit")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    elif submitted:
        generate_response(text)