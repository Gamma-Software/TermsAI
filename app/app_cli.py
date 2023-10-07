import json
import os
from app.module.chains import overall_chain_exec

# Setup langsmith variables
os.environ['LANGCHAIN_TRACING_V2'] = str(st.secrets["langsmith"]["tracing"])
os.environ['LANGCHAIN_ENDPOINT'] = st.secrets["langsmith"]["api_url"]
os.environ['LANGCHAIN_API_KEY'] = st.secrets["langsmith"]["api_key"]
os.environ['LANGCHAIN_PROJECT'] = st.secrets["langsmith"]["project"]

questions = ["Does the website collect personal information from your users?",
             #"Does the website send emails or newsletters to users?",
             #"Does the website use any digital analytics software for tracking purposes?",
             #"Does the website show ads?",
             #"Does the website use retargeting for advertising?",
             #"Is the website is offered to users under the age of 13?"
             ]
with open("terms", "r") as f:
    terms = f.read()
answers = overall_chain_exec(questions, terms)
answers = overall_chain_exec(questions, terms)

print(answers)
json.dump(answers, open("answers.json", "w+"))
