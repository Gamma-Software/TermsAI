from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/api")
async def api():
    return {"message": "API Hello World"}


@app.get("/ht")
async def health_check():
    return "ok"


class Item(BaseModel):
    url: str
    question: str


def scrap_web(url):
    """
    Scrape the web using Google API and search for terms of use of this website or any kind of policies
    """
    return "Terms of use"


@app.get("/api/terms")
async def terms(item: Item):
    return item
