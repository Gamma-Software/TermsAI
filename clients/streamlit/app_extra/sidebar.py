import os
import streamlit as st
from app_extra import description


def sidebar():
    with st.sidebar:
        if not st.secrets.get("openai_api_key"):
            openai_api_key = st.text_input(
                "OpenAI API Key", key="chatbot_api_key", type="password"
            )
            if openai_api_key and not st.session_state.get("openai_api_key"):
                st.session_state["openai_api_key"] = openai_api_key

            st.markdown(
                "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
            )
        else:
            st.session_state["openai_api_key"] = st.secrets["openai_api_key"]
        if st.session_state.get("openai_api_key"):
            os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]

        features = st.selectbox(
            "Select a feature", ["Process PDF", "Display PDF metadata"]
        )
        # How to use
        st.markdown(description.how_to_use)
        return features
