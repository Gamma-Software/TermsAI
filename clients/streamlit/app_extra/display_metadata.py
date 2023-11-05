import streamlit as st
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument


def display_pdf_metadata(pdf_file):
    parser = PDFParser(pdf_file)
    doc = PDFDocument(parser)

    for info in doc.info:
        for k, v in info.items():
            try:
                if v.decode():
                    st.write(f"{k}: {v.decode()}")
            except Exception:
                st.write(f"{k}: {v}")


def display_metadata():
    uploaded_pdf = st.file_uploader(
        "Upload contract PDFs",
        ["pdf"],
        key="pdf",
        accept_multiple_files=True,
        help="could be a picture or a pdf",
    )
    if uploaded_pdf:
        for file in uploaded_pdf:
            st.subheader(file.name)
            display_pdf_metadata(file)
