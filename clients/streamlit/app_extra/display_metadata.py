import streamlit as st
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import json


def display_pdf_metadata(pdf_file):
    parser = PDFParser(pdf_file)
    doc = PDFDocument(parser)

    for info in doc.info:
        with st.expander("See results"):
            for k, v in info.items():
                if k not in ["Questions", "Summary"]:
                    continue

                def dis(v):
                    try:
                        return v.decode()
                    except Exception:
                        return v

                if k == "Summary":
                    st.write("Summary")
                    st.caption(dis(v))
                    st.divider()
                else:
                    for k_, v_ in json.loads(dis(v)).items():
                        st.write(k_)
                        st.caption(v_)
                        st.divider()


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
