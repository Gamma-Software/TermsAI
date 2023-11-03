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
    simple_qa_chain_long,
    summarize_chain_doc_exec
)
from process_doc.process import extract_clean_doc, embedd_doc
from io import StringIO

# Setup langsmith variables
os.environ['LANGCHAIN_TRACING_V2'] = str(st.secrets["langsmith"]["tracing"])
os.environ['LANGCHAIN_ENDPOINT'] = st.secrets["langsmith"]["api_url"]
os.environ['LANGCHAIN_API_KEY'] = st.secrets["langsmith"]["api_key"]
os.environ['LANGCHAIN_PROJECT'] = st.secrets["langsmith"]["project"]

st.title("📝 Read my contract")
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
## 1) Retrieve Terms of contract
"""
data = None
if "extracted_data" not in st.session_state:
    st.session_state["extracted_data"] = None

if "vector_store" not in st.session_state:
    st.session_state["vector_store"] = None

choice = st.radio("How do you want to retrieve the Terms of the contract ?",
                  ("Upload a file", "Enter the raw text"))

if choice == "Upload a file":
    uploaded_file = st.file_uploader(
        "Upload a file (could be a picture or a pdf)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=False)
    # write the stream in a file
    if uploaded_file is not None:
        # Write it into a temp file
        temp_file = f"/tmp/{uploaded_file.name}"
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getvalue())
        # get extension
        extension = uploaded_file.name.split(".")[-1]
        if extension in ["png", "jpg", "jpeg"]:
            data = {"pic": temp_file}
        elif extension == "pdf":
            data = {"pdf": temp_file}
else:
    text = st.text_area(
        "Enter the raw text",
        st.session_state["extracted_data"] if "extracted_data" in st.session_state else "")
    if text:
        data = {"text": text}

process_button = st.button("Process data")

if process_button:
    with st.status("Processing file(s)...", expanded=True) as status:
        # We process the pdf or photo to extract the text
        # And create a vector store to each paragraph
        st.write("Extract the text from the document...")
        status.update(label="Extract the text from the document...", expanded=True)
        st.session_state["extracted_data"] = extract_clean_doc(data)

        st.write("Embed the text in vector store...")
        status.update(label="Embed the text in vector store...", expanded=True)
        st.session_state["vector_store"] = embedd_doc(st.session_state["extracted_data"])

        status.update(label="Processing complete!", state="complete", expanded=False)


if not st.session_state["extracted_data"] or not st.session_state["vector_store"]:
    st.stop()

with st.expander("Show extracted data"):
    st.write(st.session_state["extracted_data"])
"""
## 2) Questions

Now you can ask questions about the terms of use and privacy policy.
e.g:
- Does the website collect personal information from your users?
- Does the website send emails or newsletters to users?
- Does the website use any digital analytics software for tracking purposes?
- Does the website show ads?
- Does the website use retargeting for advertising?
"""
questions = st.text_area("Question ",
                        placeholder="Does the website collect personal information from your users?\nDoes the website use any digital analytics software for tracking purposes?")
questions = questions.split("\n")
answer = st.button("Answer")
if answer:
    with st.status("Answer question(s)...", expanded=True) as status:
        for id, question in enumerate(questions):
            if question == "":
                continue
            status.update(label=f"Answer question(s)... {id}/{len(questions)}", expanded=True)
            docs, answers = simple_qa_chain(question, st.session_state["vector_store"])
            #docs_2, answers_2 = simple_qa_chain_long(question, st.session_state["extracted_data"])
        #elif terms_url != "":
        #    answers = overall_chain_url_exec([question], terms_url)
        #for k, v in answers.items():
        #    question_container.markdown(v["emoji"] + v["words"])
        #    st.markdown(">" + v["output"]["answer"] + " " + v["output"]["excerpts"])
            st.write(question)
            st.caption(answers["output_text"])
            st.divider()
            #question_container.write(docs_2)
            #question_container.write(answers_2)
        status.update(label="Question(s) answered!", state="complete", expanded=True)


"""
## 3) Summarize the terms of use and privacy policy

You can summarize the terms of use and privacy policy by clicking the button below.
"""
summarize = st.button("Summarize")
if summarize:
    with st.status("Summarizing...", expanded=False) as status:
        summary = summarize_chain_doc_exec(st.session_state["extracted_data"])
        st.write(summary)
        status.update(label="Summarized!", state="complete", expanded=True)