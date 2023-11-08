"""Main Streamlit app file."""

import os
from pathlib import Path
import streamlit as st
from app_extra import sidebar, description, upload, processing, display_metadata
from process_doc.utils import generate_report

# Setup langsmith variables
os.environ["LANGCHAIN_TRACING_V2"] = str(st.secrets["langsmith"]["tracing"])
os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["langsmith"]["api_url"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["langsmith"]["api_key"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["langsmith"]["project"]


# Add sidebar
feature = sidebar.sidebar()

if feature == "Display PDF metadata":
    st.title("Display PDF metadata")
    display_metadata.display_metadata()
else:
    # Show title and description
    st.markdown(description.short_description)
    # Check if openai api key is set
    if "openai_api_key" not in st.session_state:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.divider()

    # 1. Upload a contract (or multiple ones)
    output_folder = Path("/tmp/termsai")
    raw_data = upload.upload(output_folder)
    file_upload_info = st.empty()
    st.divider()
    # 2. Ask any questions you have about the contract
    st.write("Choose the features to activate")
    c1, c2, c3 = st.columns(3)
    features_1 = c1.checkbox("Question Answering", value=True, key="qa")
    features_2 = c2.checkbox("Summary", value=True, key="summary")
    features_3 = c3.checkbox(
        "Include Metadata",
        value=(features_1 or features_2),
        disabled=(not features_1 and not features_2),
        key="metadata",
    )
    features_4 = c1.checkbox(
        "Generate report",
        value=(features_1 or features_2),
        disabled=(not features_1 and not features_2),
        key="report",
    )
    feature_selection_info = st.empty()

    QUESTIONS = None
    if features_1:
        QUESTIONS = st.text_area(
            "Enter your questions ",
            help="Enter your questions here to get answers from your contract",
            placeholder="Does the website collect personal information from your users?\nDoes the website use any digital analytics software for tracking purposes?",
            key="questions",
        )
        if QUESTIONS:
            QUESTIONS = QUESTIONS.split("\n")
    question_info = st.empty()
    st.divider()

    language = st.selectbox(
        "Select result language", ["English", "French"], key="language"
    )
    st.divider()

    # 3. Wait for the app
    zipped_processed_file = ""
    report_path = None
    execute_bt = st.button("Execute")
    if execute_bt:
        error = False
        if not raw_data:
            file_upload_info.info("Please upload a contract to continue")
            error = True
        if not features_1 and not features_2:
            feature_selection_info.info(
                "Please activate at least one feature to continue"
            )
            error = True
        if features_1 and QUESTIONS == "":
            question_info.info("Please enter at least one question to continue")
            error = True
        if error:
            st.stop()

        zipped_processed_file = processing.processing(
            QUESTIONS,
            features_1,
            features_2,
            features_3,
            raw_data,
            output_folder,
            language,
        )
        processing.display_result(output_folder)

        if features_4:
            report_path = Path("/tmp/report.csv")
            generate_report(output_folder, report_path)

    # 4. You can now download the contract with included metadata of the
    # questions and answers and the summary
    if zipped_processed_file:
        st.download_button(
            "Download the processed contract",
            data=zipped_processed_file.read_bytes(),
            file_name=zipped_processed_file.name,
            help="Download the processed contract with the metadata",
        )
    if features_4 and report_path:
        st.download_button(
            "Download report",
            data=report_path.read_bytes(),
            file_name=report_path.name,
            help="Download the report with all the results from all the PDF",
        )
