from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.parsers.pdf import extract_from_images_with_rapidocr
from langchain.document import Documents
from typing import List

def extract_doc(data) -> List[Documents]:
    if "pdf" in data:
        return [PyPDFLoader(file_path=data["pdf"]).load()]
    if "pic" in data:
        return [extract_from_images_with_rapidocr(text="Not implemented yet")]
    # Else it's raw text
    return [Documents(text=data["text"])]
