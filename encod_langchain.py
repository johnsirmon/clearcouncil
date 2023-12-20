from asyncio import as_completed
from dotenv import load_dotenv
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from datetime import datetime
from tqdm import tqdm


# Provide the relative path to the .env file
load_dotenv()

pdf_dir = 'data/PDFs'
embeddings = OpenAIEmbeddings()

# Initialize the FAISS vector store with actual parameters
faiss_store = FAISS(
    embedding_function=embeddings,  # Actual embedding function
    index="IVF1024,Flat",  # Example index type, modify according to your needs
    docstore=None,  # Example docstore, choose based on your requirement
    index_to_docstore_id=lambda x: x  # Simplest mapping, can be customized
)

splitter = CharacterTextSplitter(chunk_size=10000)

def process_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            text = ''.join([pdf_reader.pages[page_num].extract_text() for page_num in range(len(pdf_reader.pages))])
        chunks = splitter.split_text(text)
        for chunk in chunks:
            vector = embeddings.encode(chunk)
            metadata = extract_metadata(file_path)
            faiss_store.store(vector, metadata)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def extract_metadata(file_path):
    filename = os.path.basename(file_path)
    pattern = r'(\d{4}-\d{2}-\d{2}) (.*?) - (.*?)-(\d+)\.pdf'
    match = re.match(pattern, filename)
    if match:
        return {
            'meeting_date': match.group(1),
            'meeting_type': match.group(2),
            'document_type': match.group(3),
            'document_id': match.group(4)
        }
    return {}

num_files_to_process = 10
processed_files = 0

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_pdf, os.path.join(pdf_dir, filename)) 
               for filename in os.listdir(pdf_dir) 
               if filename.endswith('.pdf')]

    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing PDFs"):
        pass  # or handle results if needed

current_date = datetime.now().strftime("%Y%m%d")
index_filename = f"council_meetings_faiss_index_{current_date}.index"
save_path = os.path.join('data', 'faiss_indexes')
full_path = os.path.join(save_path, index_filename)

if not os.path.exists(save_path):
    os.makedirs(save_path)

faiss_store.save(full_path)