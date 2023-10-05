import os
import streamlit as st
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Setup langsmith variables
os.environ['LANGCHAIN_TRACING_V2'] = str(st.secrets["langsmith"]["tracing"])
os.environ['LANGCHAIN_ENDPOINT'] = st.secrets["langsmith"]["api_url"]
os.environ['LANGCHAIN_API_KEY'] = st.secrets["langsmith"]["api_key"]
os.environ['LANGCHAIN_PROJECT'] = st.secrets["langsmith"]["project"]

st.title("Terms of Use")
st.write("AI will read the terms of use and privacy policy for you and answer questions about it to synthetize the information.")

with st.sidebar:
    if ("openai_api_key" not in st.secrets or
        "openai_api_key" in st.secrets and
        st.secrets["openai_api_key"] == "your key here"):
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        if openai_api_key and 'openai_api_key' not in st.session_state:
            st.session_state['openai_api_key'] = openai_api_key
        "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    else:
        st.session_state['openai_api_key'] = st.secrets["openai_api_key"]

def json_to_markdown(json_data):
    markdown_template = ""

    for question, data in json_data.items():
        markdown_template += f"## {question}\n"
        markdown_template += f"**Answer:** {data['answer']}\n\n"
        markdown_template += f"**Excerpts:** {data['excerpts']}\n\n"

    return markdown_template


with st.form("my_form"):
    terms = st.text_area("Enter Term of use:", "")
    privacy = st.text_area("Enter Privacy Policy:", "")
    submitted = st.form_submit_button("Submit")
    if 'openai_api_key' not in st.session_state:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    elif submitted and terms != "":
        questions = """
        - Does the website collect personal information from your users?
        - Does the website send emails or newsletters to users?
        - Does the website use any digital analytics software for tracking purposes?
        - Does the website show ads?
        - Does the website use retargeting for advertising?
        - Is the website is offered to users under the age of 13?
        """
        answer = generate_response(terms, privacy)
        st.markdown(json_to_markdown(answer))

    answer = {
        "Does the website collect personal information from your users?": {
            "answer": "Yes, the website collects personal information from its users.",
            "excerpts": "Providing our Service requires collecting and using your information"
        },
        "Does the website send emails or newsletters to users?": {
            "answer": "Yes, the website may send emails or in-product notices to users.",
            "excerpts": "We may need to send you communications, like emails or in-product notices, to respond to you or inform you about any product-related issues, research, or our terms and policies."
        },
        "Does the website use any digital analytics software for tracking purposes?": {
            "answer": "The website does not explicitly mention the use of digital analytics software for tracking purposes.",
            "excerpts": ""
        },
        "Does the website show ads?": {
            "answer": "Yes, the website shows ads.",
            "excerpts": "Instead of paying to use Instagram, by using the Service covered by these Terms, you acknowledge that we show you ads that businesses and organizations pay us to promote on and off the Meta Company Products."
        },
        "Does the website use retargeting for advertising?": {
            "answer": "The website does not explicitly mention the use of retargeting for advertising.",
            "excerpts": ""
        },
        "Is the website is offered to users under the age of 13?": {
            "answer": "No, the website is not offered to users under the age of 13.",
            "excerpts": "You must be at least 13 years old."
        }
    }
    st.markdown(json_to_markdown(answer))
