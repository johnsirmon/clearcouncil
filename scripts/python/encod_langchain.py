from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API key and save it to the environment
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from PyPDF2 import PdfFileReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

# Directory containing PDFs
pdf_dir = 'path/to/pdf_folder'

# Initialize embedding and vector storage
embeddings = OpenAIEmbeddings()
faiss_store = FAISS()

# Iterate over PDF files in the directory
for filename in os.listdir(pdf_dir):
    if filename.endswith('.pdf'):
        file_path = os.path.join(pdf_dir, filename)

        # Open the PDF file
        with open(file_path, 'rb') as f:
            pdf_reader = PdfFileReader(f)
            text = ''

            # Extract text from each page
            for page_num in range(pdf_reader.numPages):
                text += pdf_reader.getPage(page_num).extractText()

        # Split text into chunks for efficient encoding
        splitter = CharacterTextSplitter(max_length=1024)  # Adjust max_length as needed
        chunks = splitter.split(text)

        # Encode each text chunk and store the resulting vector
        for chunk in chunks:
            vector = embeddings.encode(chunk)
            # Consider adding unique identifiers or metadata for each vector
            faiss_store.add(vector)
