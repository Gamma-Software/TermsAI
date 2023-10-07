import os
import streamlit as st
from app.module.chains import overall_chain_exec

# Setup langsmith variables
os.environ['LANGCHAIN_TRACING_V2'] = str(st.secrets["langsmith"]["tracing"])
os.environ['LANGCHAIN_ENDPOINT'] = st.secrets["langsmith"]["api_url"]
os.environ['LANGCHAIN_API_KEY'] = st.secrets["langsmith"]["api_key"]
os.environ['LANGCHAIN_PROJECT'] = st.secrets["langsmith"]["project"]

st.title("Terms of Use")
st.write("AI will read the terms of use and privacy policy for you and answer questions "
         "about it to synthetize the information.")

with st.sidebar:
    if "openai_api_key" not in st.secrets or "openai_api_key" in st.secrets and st.secrets["openai_api_key"] == "your key here":
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        if openai_api_key and 'openai_api_key' not in st.session_state:
            st.session_state['openai_api_key'] = openai_api_key
        "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    else:
        st.session_state['openai_api_key'] = st.secrets["openai_api_key"]

if 'openai_api_key' not in st.session_state:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

terms = st.text_area("Enter Term of use:", "")
privacy = st.text_area("Enter Privacy Policy:", "")
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
if col2.button("Answer") and question != "" and terms != "":
    answers = overall_chain_exec(st.session_state["openai_api_key"], question, terms)
    for k, v in answers.items():
        question_container.markdown(v["emoji"] + v["transformer"])
        st.markdown(">" + v["answer"] + " " + v["excerpts"])
    question_container.write(answers)
