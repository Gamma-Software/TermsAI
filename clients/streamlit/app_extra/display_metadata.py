import streamlit as st
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import json
import pandas as pd


def display_pdf_metadata(pdf_file):
    parser = PDFParser(pdf_file)
    doc = PDFDocument(parser)

    for info in doc.info:
        with st.expander("See results"):
            for k, v in info.items():
                if k not in ["Questions", "Subject"]:
                    continue

                def dis(v):
                    try:
                        return v.decode()
                    except Exception:
                        return v

                if k == "Subject":
                    st.write("Subject")
                    st.caption(dis(v))
                    st.divider()
                else:
                    for k_, v_ in json.loads(dis(v)).items():
                        st.write(k_)
                        st.caption(v_)
                        st.divider()


def get_metadata(pdf_file):
    # Display metadata in form of dataframe
    # the form of dataframe should be
    # | | Filename 1 | Filename 2 | ...
    # | Subject    | Subject1 | Subject2 | ...
    # | Question 1    | Q1 | Q2 | ...
    # | Question 2    | Q21 | Q22 | ...
    # ...
    parser = PDFParser(pdf_file)
    doc = PDFDocument(parser)
    metadata = {}
    for info in doc.info:
        for k, v in info.items():
            if k not in ["Questions", "Subject"]:
                continue
            try:
                if k == "Questions":
                    for k_, v_ in json.loads(v.decode()).items():
                        metadata[k_] = v_
                else:
                    metadata[k] = v.decode()
            except Exception:
                metadata[k] = v
    return metadata


def display_metadata():
    uploaded_pdf = st.file_uploader(
        "Upload contract PDFs",
        ["pdf"],
        key="pdf",
        accept_multiple_files=True,
        help="could be a picture or a pdf",
    )
    if uploaded_pdf:
        metadatas = {}
        for file in uploaded_pdf:
            name = file.name.replace(" ", "_")
            metadatas[name] = get_metadata(file)
            st.subheader(name)
            if metadatas[name] == {}:
                del metadatas[name]
                st.write("No metadata found")
                continue
            display_pdf_metadata(file)

        # Generate report
        if metadatas != {}:
            st.subheader("Report")
            report = pd.DataFrame(metadatas)
            st.dataframe(report, use_container_width=True)
