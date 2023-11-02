import os
from pdfminer.pdfpage import PDFPage
from pdf2image.pdf2image import convert_from_path
import ocrspace
import streamlit as st

def get_pdf_searchable_pages(file_path):
    """ Parse the pdf and result the pages that are searchable and the ones that are not """
    result = []
    page_num = 0
    with open(file_path, 'rb') as infile:
        for page_num, page in enumerate(PDFPage.get_pages(infile)):
            if page.resources is not None:
                result.append((page_num, 'Font' in page.resources.keys()))

    if page_num == 0:
        raise ValueError(f"Not a valid document")
    return result


def pdf_to_jpeg(file_path, output_path, page_id):
    """ Parse a specific page of a pdf that cannot be read into a jpeg """
    pages = convert_from_path(file_path, 200, thread_count=4, first_page=page_id, last_page=page_id)
    pages[0].save(output_path, "JPEG")
    return output_path


def extract_text_from_searchable_pdf(file_path, page_id) -> str:
    """ Extract the text from a searchable pdf """
    text = ""
    with open(file_path, 'rb') as infile:
        for page in PDFPage.get_pages(infile):
            if page.pageid == page_id:
                text = page.contents
                break
    return text


def extract_text_from_jpeg(file_path, language=ocrspace.Language.French) -> str:
    """
    Extract the text from a jpe or a pdf
    The free version of ocrspace limits for pdf:
    - 25,000 request/month
    - 1mb/file -> raise error
    - 3 pages/pdf -> raise error
    """
    # check the size of the file
    if os.path.getsize(file_path) > 1000000:
        raise ValueError("The file is too big to be processed")
    # check the number of pages
    pages = convert_from_path(file_path, 200, thread_count=4)
    if len(pages) > 3:
        raise ValueError("The file has too many pages to be processed")

    api = ocrspace.API(
        endpoint=st.secrets["ocrspace"]["endpoint"],
        api_key=st.secrets["ocrspace"]["api_key"],
        language=language)
    return api.ocr_file(file_path)