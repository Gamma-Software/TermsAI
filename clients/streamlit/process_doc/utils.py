from pdfminer.pdfpage import PDFPage
from pdf2image import convert_from_path
import easyocr


def get_pdf_searchable_pages(file_path):
    """ Parse the pdf and result the pages that are searchable and the ones that are not """
    result = []
    with open(file_path, 'rb') as infile:
        for page_num, page in enumerate(PDFPage.get_pages(infile)):
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


def extract_text_from_jpeg(file_path, lang=['fr','en'], gpu=False) -> str:
    reader = easyocr.Reader(lang, gpu=gpu) # this needs to run only once to load the model into memory
    result = reader.readtext(file_path)
