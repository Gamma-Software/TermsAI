import os
import streamlit as st
import requests


def get_token(username: str, password: str) -> str:
    """Get token from backend API"""

    url = "http://localhost:83/api/v1/login/access-token"
    payload = "grant_type=&username={}&password={}&scope=&client_id=&client_secret=".format(username, password)
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()["access_token"]

def overall_chain_exec(questions, text):
    raise NotImplementedError("Not implemented yet")
    pass

def add_task_summarize_chain_exec(bearer_token, text):
    """ Add a task to the summarize chain execution queue """
    with open("tmp.txt", "w") as f:
        f.write(text)
    url = "http://192.168.1.34:83/api/v1/summarize/file"
    payload = {}
    files = [
        ('file', open("tmp.txt", 'rb'))
    ]
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {}'.format(bearer_token),
        'Content-Type': 'type=text/plain'
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    os.remove("tmp.txt")
    json_response = response.json()
    if response.status_code != 200:
        raise Exception("Error: {}".format(json_response))
    return json_response["result"]["task_id"]

def get_task_summarize_chain_exec_result(bearer_token, task_id):
    """curl -X 'GET' \
  'http://192.168.1.34:83/api/v1/summarize/task?id=0' \
  -H 'accept: application/json'"""
    url = "http://localhost:83/api/v1/summarize/task?id={}".format(task_id)
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {}'.format(bearer_token),
    }
    response = requests.request("GET", url, headers=headers)
    json_response = response.json()
    if response.status_code != 200:
        raise Exception("Error: {}".format(json_response))
    return json_response["result"]

st.set_page_config(layout="wide")

#from redis import Redis
#from langchain.cache import RedisCache
#langchain.llm_cache = RedisCache(redis_=Redis(host=st.secrets["redis"]["host"],
#                                              port=st.secrets["redis"]["port"], db=0))

with st.sidebar:
    user = st.text_input("Username", value="")
    password = st.text_input("Password", value="", type="password")
    token = None
    if user and password:
        token = get_token(user, password)
    choice = st.selectbox("Menu", ["question/answer", "summarize"])

if not token:
    st.write("Enter username and password to get started.")
    st.stop()


st.title("Terms of Use")
st.write("AI will read the terms of use and privacy policy for you and answer questions "
         "about it to synthetize the information.")

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
                task_id = add_task_summarize_chain_exec(token, terms)
            #elif terms_url != "":
            #    summary = summarize_chain_url_exec(terms_url)
            got_summary = False
            while not got_summary:
                try:
                    summary = get_task_summarize_chain_exec_result(token, task_id)
                except Exception as e:
                    pass
                if summary:
                    got_summary = True
                    break
            st.write(summary)
