import sys
sys.path.append(r"C:\Users\SHUBHAM\projects\udemy-KN\2_rag\backend")
from utils.constants import PERSIST_DIRECTORY, DATA_FOLDER
from utils.utils import get_embedding_model, get_logger, timeit

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_chroma import Chroma


import time
import pdfplumber
import os

logger = get_logger()


def table_to_markdown(table):
    """Convert a table (list of lists) to a Markdown table.

    Args:
        table (list): A list of lists representing the table.

    Returns:
        str: The Markdown representation of the table.
    """
    markdown = "| " + " | ".join(map(str, table[0])) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(table[0])) + " |\n"
    for row in table[1:]:
        markdown += "| " + " | ".join(map(str, row)) + " |\n"
    return markdown


@timeit
def extract_text_and_tables(pdf_path):
    """Extract text and tables from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        tuple: A tuple containing the extracted text documents and tables.
    """
    # Text extraction
    loader = PyPDFLoader(pdf_path)
    text_docs = loader.load()

    # Table extraction
    with pdfplumber.open(pdf_path) as pdf:
        tables = []
        for page in pdf.pages:
            for table in page.extract_tables():
                tables.append({"table": table, "page": page.page_number})
    return text_docs, tables


@timeit
def read_all_data(path_to_data_folder):
    """Read all PDF files in a folder and extract text and tables.

    Args:
        path_to_data_folder (str): The path to the folder containing PDF files.

    Returns:
        tuple: A tuple containing all extracted text documents and tables.
    """
    list_text_docs = []
    list_tables = []
    for file_name in os.listdir(path_to_data_folder):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(path_to_data_folder, file_name)
            logger.info(f"Processing file: {file_name}")
            text_docs, tables = extract_text_and_tables(pdf_path)
            logger.info(f"Extracted {len(text_docs)} text documents and {len(tables)} tables from {file_name}")
            list_text_docs.extend(text_docs)
            list_tables.extend(tables)
    return list_text_docs, list_tables


@timeit
def split_text_data(text_docs):
    """Split text documents into smaller chunks.

    Args:
        text_docs (list): A list of text documents.

    Returns:
        list: A list of split text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    split_texts = text_splitter.split_documents(text_docs)
    return split_texts


@timeit
def split_table_data(list_of_tables):
    """Split table data into smaller chunks.

    Args:
        list_of_tables (list): A list of tables.

    Returns:
        list: A list of split table chunks.
    """
    table_docs = []
    for table in list_of_tables:
        table_md = table_to_markdown(table["table"])
        table_docs.append({
            "page": table["page"],
            "content": table_md
        })
    return table_docs


@timeit
def get_split_data(text_docs, tables):
    """
    Split text documents and tables into smaller chunks.

    Args:
        text_docs (list): A list of text documents.
        tables (list): A list of tables.

    Returns:
        list: A list of split documents.
    """
    split_texts = split_text_data(text_docs)
    split_tables = split_table_data(tables)

    all_docs = []

    # Add text chunks
    for d in split_texts:
        all_docs.append(Document(page_content=d.page_content, metadata=d.metadata))

    # Add tables
    for t in split_tables:
        all_docs.append(Document(page_content=t["content"], metadata={"page": t["page"], "type": "table"}))
    return all_docs


@timeit
def create_vector_store(all_docs, embedding_model, persist_directory):
    vs = Chroma.from_documents(documents=all_docs, embedding=embedding_model, persist_directory=persist_directory)
    return vs


@timeit
def ingest_data(path_to_data_folder=DATA_FOLDER, persist_directory=PERSIST_DIRECTORY):
    """Ingest data from PDF files and create a vector store.

    Args:
        path_to_data_folder (str, optional): The path to the folder containing PDF files. Defaults to DATA_FOLDER.
        persist_directory (str, optional): The path to the directory for persisting the vector store. Defaults to PERSIST_DIRECTORY.
    """
    text_docs, tables = read_all_data(path_to_data_folder)
    all_docs = get_split_data(text_docs, tables)
    embedding_model = get_embedding_model()
    create_vector_store(all_docs, embedding_model, persist_directory)
    return

def test():
    logger.info("Starting test...")
    

if __name__ == "__main__":
    ingest_data()