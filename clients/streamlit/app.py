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
from process_doc.utils import integrated_metadata_in_pdf
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

    features = st.radio("Use cases", ("Question Answering", "Summarization", "Integrate Metadata"))

if 'openai_api_key' not in st.session_state:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

data = None
if "extracted_data" not in st.session_state:
    st.session_state["extracted_data"] = None

if "vector_store" not in st.session_state:
    st.session_state["vector_store"] = None

if features != "Integrate Metadata":
    choice = st.radio("How do you want to retrieve the Terms of the contract ?",
                    ("Upload a file", "Enter the raw text"))
else:
    choice = "Upload a file"

if choice == "Upload a file":
    uploaded_file = st.file_uploader(
        "Upload contract PDFs" if features == "Integrate Metadata" else "Upload a file",
        type=["pdf"] if features == "Integrate Metadata" else ["pdf", "png", "jpg", "jpeg", "txt"],
        accept_multiple_files=features == "Integrate Metadata",
        help="could be a picture or a pdf")
    # write the stream in a file
    if uploaded_file is not None and uploaded_file != []:
        def treat_file(file):
            # Write it into a temp file
            temp_file = f"/tmp/{file.name}"
            with open(temp_file, "wb") as f:
                f.write(file.getvalue())
            # get extension
            extension = file.name.split(".")[-1]
            if extension in ["png", "jpg", "jpeg"]:
                return {"pic": temp_file}
            elif extension == "pdf":
                return {"pdf": temp_file}
        if isinstance(uploaded_file, list):
            data = [treat_file(f) for f in uploaded_file]
        else:
            data = {"pdf": treat_file(uploaded_file)}

else:
    text = st.text_area(
        "Enter the raw text",
        st.session_state["extracted_data"] if "extracted_data" in st.session_state else "")
    if text:
        data = {"text": text}

if features == "Question Answering":
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
    questions = st.text_area("Question ",
                            placeholder="Does the website collect personal information from your users?\nDoes the website use any digital analytics software for tracking purposes?")
    questions = questions.split("\n")
    button_ = st.button("Answer")

if features == "Summarization":
    """
    ## Summarize the terms of use and privacy policy

    You can summarize the terms of use and privacy policy by clicking the button below.
    """
    button_ = st.button("Summarize")

if features == "Integrate Metadata":
    """
    This feature will allow to ask questions about your contracts and add the result in the metadata.

    ## Questions

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
    button_ = st.button("Execute")

if button_:
    with st.status("Processing file(s)...", expanded=True) as status:
        def process_file(file, id, length):
            # We process the pdf or photo to extract the text
            # And create a vector store to each paragraph
            st.write(f"Extract the text from the document... {id}/{length}")
            status.update(label="Extract the text from the document...", expanded=True)
            st.session_state["extracted_data"] = extract_clean_doc(file)

            st.write("Embed the text in vector store...")
            status.update(label=f"Embed the text in vector store... {id}/{length}", expanded=True)
            st.session_state["vector_store"] = embedd_doc(st.session_state["extracted_data"])

            if not st.session_state["extracted_data"] or not st.session_state["vector_store"]:
                st.stop()
                status.update(label="Processing of files failed !", state="error", expanded=False)

            def summarize():
                status.update(label="Summarizing...", state="running", expanded=True)
                summary = summarize_chain_doc_exec(st.session_state["extracted_data"])
                st.write(summary)
                status.update(label="Summarized!", state="complete", expanded=True)
                return summary

            def answer_question():
                result = []
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
                    result.append((question, answers["output_text"]))
                return result

            if features == "Summarization":
                summarize()

            if features == "Question Answering":
                answer_question()

            if features == "Integrate Metadata":
                summary = summarize()
                answers_of_question = answer_question()
                metadata = {
                    "summary": summary,
                    "questions": [
                        {
                            "question": q,
                            "answer": a
                        } for q, a in answers_of_question
                    ]
                }
                # Integrate the metadata
                integrated_metadata_in_pdf(file, metadata)

        if isinstance(data, list):
            for id, file in enumerate(data):
                process_file(file, id+1, len(data))
        else:
            process_file(data, 1, 1)
        status.update(label="Question(s) answered!", state="complete", expanded=True)


        # We process the pdf or photo to extract the text
        # And create a vector store to each paragraph
        st.write("Extract the text from the document...")
        status.update(label="Extract the text from the document...", expanded=True)
        st.session_state["extracted_data"] = extract_clean_doc(data)

        st.write("Embed the text in vector store...")
        status.update(label="Embed the text in vector store...", expanded=True)
        st.session_state["vector_store"] = embedd_doc(st.session_state["extracted_data"])

        if not st.session_state["extracted_data"] or not st.session_state["vector_store"]:
            st.stop()
            status.update(label="Processing of files failed !", state="error", expanded=False)

        if features == "Summarization":
            status.update(label="Summarizing...", state="running", expanded=True)
            summary = summarize_chain_doc_exec(st.session_state["extracted_data"])
            st.write(summary)
            status.update(label="Summarized!", state="complete", expanded=True)

        if features == "Question Answering":
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

