from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API key and save it to the environment
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


import os
from PyPDF2 import PdfFileReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

# Directory containing PDFs
pdf_dir = 'path/to/pdf_folder'

# Initialize embedding and vector storage
embeddings = OpenAIEmbeddings()
faiss_store = FAISS()

# Iterate over PDF files
for filename in os.listdir(pdf_dir):
    if filename.endswith('.pdf'):
        file_path = os.path.join(pdf_dir, filename)

        # Read PDF and extract text
        with open(file_path, 'rb') as f:
            pdf_reader = PdfFileReader(f)
            text = ''
            for page_num in range(pdf_reader.numPages):
                text += pdf_reader.getPage(page_num).extractText()

        # Split text into chunks
        splitter = CharacterTextSplitter(max_length=1024)  # Adjust max_length as needed
        chunks = splitter.split(text)

        # Encode and store each chunk
        for chunk in chunks:
            vector = embeddings.encode(chunk)
            faiss_store.add(vector)  # May need additional handling for IDs or metadata






