import process_doc.ocrspace_api as ocrspace

import os
from pdfminer.pdfpage import PDFPage
from pdf2image.pdf2image import convert_from_path
import streamlit as st
from typing import List
from process_doc.utils import split_pdf_every, split_pdf, convert_pdf_to_searchable

print(convert_pdf_to_searchable("amelie_merged.pdf", "amelie_merged.pdf"))
exit()

api = ocrspace.API(
    endpoint="https://api.ocr.space/parse/image",
    api_key="K81678992188957",
    language=ocrspace.Language.French)
stream_pdf = api.ocr_file_to_pdf("pdf.pdf")
with open("test.pdf", "wb") as f:
    f.write(stream_pdf)