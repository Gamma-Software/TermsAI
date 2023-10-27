from pydantic import BaseModel
from fastapi import UploadFile, File


class QuestionText(BaseModel):
    terms: str
    question: str


class QuestionFile(BaseModel):
    question: str


class QuestionUrl(BaseModel):
    url: str
    question: str