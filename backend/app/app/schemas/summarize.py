from pydantic import BaseModel
from fastapi import UploadFile, File


class SummarizeText(BaseModel):
    text: str


class SummarizeFile(BaseModel):
    file: UploadFile = File(...)


class SummarizeUrl(BaseModel):
    url: str
