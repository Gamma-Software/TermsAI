from pydantic import BaseModel, Field
from typing import List
from fastapi import UploadFile, File


class SummarizeText(BaseModel):
    text: str

class SummarizeFile(BaseModel):
    files: UploadFile = File(...)

class SummarizeUrl(BaseModel):
    url: str
