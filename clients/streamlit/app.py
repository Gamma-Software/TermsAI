import os
import streamlit as st
from chains import (
    overall_chain_exec,
    overall_summarize_chain_exec,
    overall_summarize_chain_url_exec,
    overall_chain_url_exec,
    summarize_chain_url_exec,
    summarize_chain_exec,
    simple_qa_chain,
    simple_qa_chain_long
)
from process_doc.process import extract_clean_doc, embedd_doc
from io import StringIO

# Setup langsmith variables
os.environ['LANGCHAIN_TRACING_V2'] = str(st.secrets["langsmith"]["tracing"])
os.environ['LANGCHAIN_ENDPOINT'] = st.secrets["langsmith"]["api_url"]
os.environ['LANGCHAIN_API_KEY'] = st.secrets["langsmith"]["api_key"]
os.environ['LANGCHAIN_PROJECT'] = st.secrets["langsmith"]["project"]

st.title("Read my contract")
st.write("This application will read you contract and answer to any question you might have.")

with st.sidebar:
    if "openai_api_key" not in st.secrets:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        if openai_api_key and 'openai_api_key' not in st.session_state:
            st.session_state['openai_api_key'] = openai_api_key
        "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    else:
        st.session_state['openai_api_key'] = st.secrets["openai_api_key"]
    if "openai_api_key" in st.session_state:
        os.environ['OPENAI_API_KEY'] = st.session_state['openai_api_key']

if 'openai_api_key' not in st.session_state:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

"""
## 1/3 Retrieve contract

Do you want to upload a PDF, a photo or enter the raw text?
"""

choice = st.selectbox("Select", ("Raw text", "PDF", "Photo"))
data = None
if "extracted_data" not in st.session_state:
    st.session_state["extracted_data"] = None

if "vector_store" not in st.session_state:
    st.session_state["vector_store"] = None

if choice == "Raw text":
    text = st.text_area("Enter the raw text:", st.session_state["extracted_data"] if "extracted_data" in st.session_state else "")
    if text:
        data = {"text": text}

if choice == "PDF":
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    # write the stream in a file
    if uploaded_file is not None:
        # Write it into a temp file
        temp_file = "/tmp/temp.pdf"
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getvalue())
        data = {"pdf": temp_file}

if choice == "Photo":
    pic = st.file_uploader("Upload a photo", type=["png", "jpg", "jpeg"])
    if pic:
        data = {"pic": pic}

process_button = st.button("Process data")

if not data:
    st.stop()

if process_button:
    with st.spinner("Processing..."):
        # We process the pdf or photo to extract the text
        # And create a vector store to each paragraph
        st.session_state["extracted_data"] = extract_clean_doc(data)
        st.write(st.session_state["extracted_data"])
        st.session_state["vector_store"] = embedd_doc(st.session_state["extracted_data"])


if not st.session_state["extracted_data"] or not st.session_state["vector_store"]:
    st.stop()

with st.expander("Show extracted data"):
    st.write(st.session_state["extracted_data"])

"""
## 2/3 Questions
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
    if st.session_state["vector_store"] != None:
        docs, answers = simple_qa_chain(question, st.session_state["vector_store"])
        #docs_2, answers_2 = simple_qa_chain_long(question, st.session_state["extracted_data"])
    #elif terms_url != "":
    #    answers = overall_chain_url_exec([question], terms_url)
    #for k, v in answers.items():
    #    question_container.markdown(v["emoji"] + v["words"])
    #    st.markdown(">" + v["output"]["answer"] + " " + v["output"]["excerpts"])
        with st.expander("Docs"):
            question_container.write(docs)
        question_container.write(answers["output_text"])
        #question_container.write(docs_2)
        #question_container.write(answers_2)

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