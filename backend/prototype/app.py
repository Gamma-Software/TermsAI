import os
import streamlit as st
from backend.app.app.llm.chains import (
    overall_chain_exec,
    overall_summarize_chain_exec,
    overall_summarize_chain_url_exec,
    overall_chain_url_exec,
    summarize_chain_url_exec,
    summarize_chain_exec
)

# Setup langsmith variables
import langchain
langchain.debug = st.secrets["langchain"]["debug"]
langchain.debug = True
#from redis import Redis
#from langchain.cache import RedisCache
#langchain.llm_cache = RedisCache(redis_=Redis(host=st.secrets["redis"]["host"],
#                                              port=st.secrets["redis"]["port"], db=0))
os.environ['OPENAI_API_KEY'] = st.secrets["openai_api_key"]
os.environ['LANGCHAIN_TRACING_V2'] = str(st.secrets["langsmith"]["tracing"])
os.environ['LANGCHAIN_ENDPOINT'] = st.secrets["langsmith"]["api_url"]
os.environ['LANGCHAIN_API_KEY'] = st.secrets["langsmith"]["api_key"]
os.environ['LANGCHAIN_PROJECT'] = st.secrets["langsmith"]["project"]

st.title("Terms of Use")
st.write("AI will read the terms of use and privacy policy for you and answer questions "
         "about it to synthetize the information.")

with st.sidebar:
    if "openai_api_key" not in st.secrets or "openai_api_key" in st.secrets:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        if openai_api_key and 'openai_api_key' not in st.session_state:
            st.session_state['openai_api_key'] = openai_api_key
        "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    else:
        st.session_state['openai_api_key'] = st.secrets["openai_api_key"]

    choice = st.selectbox("Menu", ["question/answer", "summarize"])

if 'openai_api_key' not in st.session_state:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

terms = st.text_area("Enter Terms of use:", "")
terms_url = st.text_area("Or enter Terms of use from URL", "")
#privacy = st.text_area("Enter Privacy Policy:", "")

if choice == "question/answer":
    """
    ## Questions
    Now you can ask questions about the terms of use and privacy policy.
    e.g:
    - Does the website collect personal information from your users?
    - Does the website send emails or newsletters to users?
    - Does the website use any digital analytics software for tracking purposes?
    - Does the website show ads?
    - Does the website use retargeting for advertising?
    """
    question_container = {}
    question_container = st.container()
    col1, col2 = question_container.columns([0.75, 0.25])
    question = col1.text_input("Question ", value="")
    if col2.button("Answer"):
        if terms != "":
            answers = overall_chain_exec([question], terms)
        elif terms_url != "":
            answers = overall_chain_url_exec([question], terms_url)
        for k, v in answers.items():
            question_container.markdown(v["emoji"] + v["words"])
            st.markdown(">" + v["output"]["answer"] + " " + v["output"]["excerpts"])
        question_container.write(answers)

if choice == "summarize":
    """
    ## Summarize the terms of use and privacy policy

    You can summarize the terms of use and privacy policy by clicking the button below.
    """
    if st.button("Summarize"):
        with st.spinner("Summarizing..."):
            if terms != "":
                summary = summarize_chain_exec(terms)
            elif terms_url != "":
                summary = summarize_chain_url_exec(terms_url)
            st.write(summary)
