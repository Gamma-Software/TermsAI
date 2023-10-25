from pydantic import BaseModel
from fastapi import UploadFile, File


class QuestionText(BaseModel):
    text: str


class QuestionFile(BaseModel):
    file: UploadFile = File(...)


class QuestionUrl(BaseModel):
    url: str
