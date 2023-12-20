from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Importing required functionalities
from PyPDF2 import PdfFileReader, PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from typing_extensions import Concatenate

# Set up the OpenAI API key

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# Extract text from a given PDF file
def extract_pdf_text(file_path):
    pdf_file = PdfFileReader(file_path)
    text_data = ''
    for pg in pdf_file.pages:
        text_data += pg.extractText()
    return text_data

pdf_text = extract_pdf_text('path_to_your_pdf.pdf')



