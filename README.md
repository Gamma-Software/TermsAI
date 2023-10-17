# TermsAI
This project is meant to read the term of use for you and get the most important informations of it. It uses the power of Large Language Models to do so.

## How it works

1. The user will enter a website
2. the app scrape internet to get the term of use of this website
    - By searching using Google API and searching for `url + " term of use"`
3. The term of use is then sent to a large language model to answer the question
