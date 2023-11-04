import os
import streamlit as st


def sidebar():
    with st.sidebar:
        if "openai_api_key" not in st.secrets:
            openai_api_key = st.text_input(
                "OpenAI API Key", key="chatbot_api_key", type="password"
            )
            if openai_api_key and "openai_api_key" not in st.session_state:
                st.session_state["openai_api_key"] = openai_api_key

            st.markdown(
                "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
            )
        else:
            st.session_state["openai_api_key"] = st.secrets["openai_api_key"]
        if "openai_api_key" in st.session_state:
            os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]
