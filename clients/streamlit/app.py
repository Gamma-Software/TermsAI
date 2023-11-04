"""Main Streamlit app file."""

import os
import streamlit as st
from app_extra import sidebar, description, upload, processing

# Setup langsmith variables
os.environ["LANGCHAIN_TRACING_V2"] = str(st.secrets["langsmith"]["tracing"])
os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["langsmith"]["api_url"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["langsmith"]["api_key"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["langsmith"]["project"]

# Show title and description
st.markdown(description.short_description)

# How to use
with st.expander("User guide"):
    st.markdown(description.how_to_use)

# Add sidebar
sidebar.sidebar()

# Check if openai api key is set
if "openai_api_key" not in st.session_state:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

st.divider()

# 1. Upload a contract (or multiple ones)
raw_data = upload.upload()
file_upload_info = st.empty()
st.divider()
# 2. Ask any questions you have about the contract
st.write("Choose the features to activate")
c1, c2, c3 = st.columns(3)
features_1 = c1.checkbox("Question Answering", value=True)
features_2 = c2.checkbox("Summary", value=True)
features_3 = c3.checkbox(
    "Include Metadata",
    value=(features_1 or features_2),
    disabled=(not features_1 and not features_2),
)
feature_selection_info = st.empty()

QUESTIONS = None
if features_1:
    QUESTIONS = st.text_area(
        "Enter your questions ",
        help="Enter your questions here to get answers from your contract",
        placeholder="Does the website collect personal information from your users?\nDoes the website use any digital analytics software for tracking purposes?",
    )
    if QUESTIONS:
        QUESTIONS = QUESTIONS.split("\n")
question_info = st.empty()
st.divider()

# 3. Wait for the app
processed_filepath = None
if st.button("Execute"):
    if not (raw_data and (features_1 and QUESTIONS)):
        if not raw_data:
            file_upload_info.info("Please upload a contract to continue")
        if not features_1 and not features_2:
            feature_selection_info.info(
                "Please activate at least one feature to continue"
            )
        if QUESTIONS == "":
            question_info.info("Please enter at least one question to continue")
    else:
        processed_filepath = processing.processing(
            QUESTIONS, features_1, features_2, features_3, raw_data
        )

# 4. You can now download the contract with included metadata of the questions and answers and the summary
if processed_filepath:
    st.download_button(
        "Download the processed contract",
        processed_filepath,
        help="Download the processed contract with the metadata and summary",
    )
