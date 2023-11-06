from datetime import datetime
import os
from os import mkdir
import shutil
from typing import List
from pdfminer.pdfpage import PDFPage
from pdf2image.pdf2image import convert_from_path
import process_doc.ocrspace_api as ocrspace
import streamlit as st
import PyPDF2
import pdfplumber
import json

# endpoint=st.secrets["ocrspace"]["endpoint"],
# api_key=st.secrets["ocrspace"]["api_key"],
endpoint = "https://api.ocr.space/parse/image"
api_key = "K81678992188957"


def get_pdf_searchable_pages(file_path):
    """Parse the pdf and result the pages that are searchable and the ones that are not
    If false -> the page is not searchable"""
    result = []
    page_num = None
    with open(file_path, "rb") as infile:
        for page_num, page in enumerate(PDFPage.get_pages(infile)):
            if page.resources is not None:
                result.append((page_num, "Font" in page.resources.keys()))

    if page_num is None:
        raise ValueError("Not a valid document")
    return result


def get_pdf_number_pages(file_path):
    with pdfplumber.open(file_path) as pdf:
        length = len(pdf.pages)
    return length


def pdf_to_jpeg(file_path, output_path, page_id):
    """Parse a specific page of a pdf that cannot be read into a jpeg"""
    pages = convert_from_path(
        file_path, 200, thread_count=4, first_page=page_id, last_page=page_id
    )
    pages[0].save(output_path, "JPEG")
    return output_path


def extract_text_from_searchable_pdf(file_path, page_id) -> str:
    """Extract the text from a searchable pdf"""
    with pdfplumber.open(file_path) as pdf:
        text_to_return = pdf.pages[page_id].extract_text()
    # remove wathermark (remove last line)
    text_to_return = "\n".join(text_to_return.split("\n")[:-1])
    return text_to_return


def extract_text_from_jpeg(file_path, language=ocrspace.Language.French) -> str:
    """
    Extract the text from a jpeg or png
    The free version of ocrspace limits for jpeg:
    - 25,000 request/month
    - 1mb/file -> raise error
    - 3 pages/pdf -> raise error
    """
    # check the size of the file
    if os.path.getsize(file_path) > 1000000:
        raise ValueError("The file is too big to be processed")

    api = ocrspace.API(
        endpoint=st.secrets["ocrspace"]["endpoint"],
        api_key=st.secrets["ocrspace"]["api_key"],
        language=language,
    )
    return api.ocr_file(file_path)


def make_pdf_searchable(
    file_path, output_path, language=ocrspace.Language.French, to_disk=False
):
    """
    Extract the text from a jpe or a pdf
    The free version of ocrspace limits for pdf:
    - 25,000 request/month
    - 1mb/file -> raise error
    - 3 pages/pdf -> raise error
    The file must be a pdf otherwise it will raise an error
    """
    # check the size of the file
    if os.path.getsize(file_path) > 1000000:
        raise ValueError("The file is too big to be processed")
    # check the number of pages
    with pdfplumber.open(file_path) as pdf:
        if len(pdf.pages) > 3:
            raise ValueError("The file has too many pages to be processed")
    # Check extension
    if not file_path.endswith(".pdf"):
        raise ValueError("The file is not a pdf")

    api = ocrspace.API(endpoint, api_key, language=language)
    stream = api.ocr_file_to_pdf(file_path)
    if to_disk:
        with open(output_path, "wb") as f:
            f.write(stream)
    return stream


def split_pdf(
    input_pdf_path, output_pdf_path, start_page, end_page
) -> PyPDF2.PdfWriter:
    if start_page == end_page:
        raise ValueError("The start page and end page cannot be the same")
    pdf_writer = PyPDF2.PdfWriter()
    try:
        pdf_file = open(input_pdf_path, "rb")
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        if start_page < 0:
            start_page = 0

        if end_page > len(pdf_reader.pages):
            end_page = len(pdf_reader.pages)

        for page_num in range(start_page, end_page):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

        with open(output_pdf_path, "wb") as output_pdf_file:
            pdf_writer.write(output_pdf_file)

        pdf_file.close()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return pdf_writer


def split_pdf_every(input_pdf, output_pdf_suffix, every) -> List[str]:
    output_list = []
    try:
        pdf_file = open(input_pdf, "rb")
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        input_dir = os.path.dirname(input_pdf)

        for page_num, _ in enumerate(pdf_reader.pages):
            if page_num % every == 0:
                pdf_writer = PyPDF2.PdfWriter()
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)
                output_list.append(
                    os.path.join(input_dir, f"{output_pdf_suffix}{page_num}.pdf")
                )
                with open(output_list[-1], "wb") as output_pdf_file:
                    pdf_writer.write(output_pdf_file)
                pdf_writer.close()
        pdf_file.close()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return output_list


def merge_pdf(input_pdfs, output_pdf) -> str:
    """Merge multiple pdfs into one pdf"""
    merger = PyPDF2.PdfMerger()
    for pdf in input_pdfs:
        merger.append(pdf)
    merger.write(output_pdf)
    return output_pdf


def convert_pdf_to_searchable(file_path, output_path):
    searchable_pages = get_pdf_searchable_pages(file_path)
    if not searchable_pages:
        raise ValueError("Not a valid document")

    # Create a temp folder
    try:
        mkdir("tmp_pdf")
    except FileExistsError:
        pass
    merger = PyPDF2.PdfMerger()
    for page, is_searchable in searchable_pages:
        print(f"Processing page {page}")
        split_out = f"tmp_pdf/temp{page}.pdf"
        split_pdf(file_path, split_out, page, page + 1)
        if not is_searchable:
            print(f"    Page {page} not searchable make OCR")
            output_ocr = f"tmp_pdf/temp{page}_ocr.pdf"
            make_pdf_searchable(split_out, output_ocr, to_disk=True)
            print(f"    Page {page} processed")
            merger.append(PyPDF2.PdfReader(output_ocr))
        else:
            merger.append(PyPDF2.PdfReader(split_out))
    merger.write(output_path)
    shutil.rmtree("tmp_pdf", ignore_errors=True)
    return searchable_pages


def integrated_metadata_in_pdf(file_path, data):
    """Add metadata to a pdf"""
    pdf_writer = PyPDF2.PdfWriter()
    pdf_reader = PyPDF2.PdfReader(file_path["pdf"])
    for _, page in enumerate(pdf_reader.pages):
        page.merge_page(page)
        pdf_writer.add_page(page)

    # Handle use case, when the user has already added questions metadata
    current_meta = pdf_reader.metadata
    if "/Questions" in current_meta:
        current_questions = json.loads(current_meta["/Questions"])
        for k, v in json.loads(data["/Questions"]).items():
            current_questions[k] = v
        data["/Questions"] = json.dumps(current_questions)

    now = datetime.now()
    pdf_datestamp = now.strftime("D:%Y%m%d%H%M%S-8'00'")
    data["/Title"] = "Contract"
    data["/ModDate"] = pdf_datestamp
    data["/Producer"] = "TermsAI"
    pdf_writer.add_metadata(data)
    with open(file_path["pdf"], "wb") as output_pdf_file:
        pdf_writer.write(output_pdf_file)
    return file_path["pdf"]
