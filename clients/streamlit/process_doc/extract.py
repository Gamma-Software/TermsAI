from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.schema.vectorstore import VectorStoreRetriever
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from utils import (
    perf_time, get_pdf_searchable_pages, extract_text_from_searchable_pdf,
    pdf_to_jpeg, extract_text_from_jpeg)

from typing import List
import re


def extract_clean_doc(data) -> List[Document]:
    """
    This function extract the text from any form of documents and cleans it.
    It keeps maximum 2 consecutive new lines and split the document into paragraphs.
    """
    if not data or "text" not in data and "pdf" not in data and "pic" not in data:
        raise ValueError("No data provided")

    paragraph_splitter = CharacterTextSplitter(separator="\n\n", keep_separator=True,
                                               add_start_index=True, chunk_size=1000,
                                               chunk_overlap=0)
    extracted_docs: List[Document] = []
    remove_extra_newlines = re.compile(r'\n{3,}', re.MULTILINE)

    if "pdf" in data:
        # First get the pages that can be searched and those not
        searchable_pages = get_pdf_searchable_pages(data["pdf"])
        for page_id, page in enumerate(searchable_pages):
            # In case the page is searchable, we extract the text
            if page[1]:
                content = extract_text_from_searchable_pdf(page[0], page_id)
            # In case the page is not searchable, we convert it to jpeg and extract the text
            else:
                jpeg_file_name = pdf_to_jpeg(data["pdf"], "/tmp/temp.jpg", page_id)
                content = extract_text_from_jpeg(jpeg_file_name)
            extracted_docs.append(Document(
                page_content=remove_extra_newlines.sub("\n\n", content),
                metadata={"type": "pdf"}))

        for pages_doc in PyPDFLoader(file_path=data["pdf"], extract_images=True).load():
            pages_doc.metadata["type"] = "pdf"
            extracted_docs.append(Document(
                page_content=remove_extra_newlines.sub("\n\n", pages_doc.page_content),
                metadata=pages_doc.metadata))

    if "pic" in data:
        raise NotImplementedError("Image extraction not implemented yet")
    if "text" in data:
        clean_text = remove_extra_newlines.sub("\n\n", data["text"])
        extracted_docs = [Document(page_content=clean_text, metadata={"type": "text"})]

    # Split the document into paragraphs
    extracted_docs = paragraph_splitter.split_documents(extracted_docs)
    return extracted_docs

@perf_time
def embedd_doc(docs: List[Document]) -> VectorStoreRetriever:
    embeddings = OpenAIEmbeddings()
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    docsearch = Chroma.from_texts(texts, embeddings, metadatas=metadatas).as_retriever()
    return docsearch