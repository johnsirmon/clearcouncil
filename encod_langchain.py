from dotenv import load_dotenv
import os
import re
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfFileReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Provide the relative path to the .env file
load_dotenv()

pdf_dir = 'data/PDFs'
embeddings = OpenAIEmbeddings()
#initialize the FAISS vector store
faiss_store = FAISS(
    embedding_function=None,  # You should provide the actual embedding function here
    index=None,  # You should provide the actual index object here
    docstore=None,  # You should provide the actual docstore object here
    index_to_docstore_id=None  # You should provide the actual index_to_docstore_id function here
)
# create a splitter to split the text into chunks of 1024 characters (OpenAI's max input length
# for the API
splitter = CharacterTextSplitter(max_length=1024)

def process_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PdfFileReader(f)
            text = ''.join([pdf_reader.getPage(page_num).extractText() for page_num in range(pdf_reader.numPages)])
        chunks = splitter.split(text)
        for chunk in chunks:
            vector = embeddings.encode(chunk)
            # Extract metadata from filename
            metadata = extract_metadata(file_path)
            # Store vector with metadata 
            faiss_store.store(vector, metadata)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def extract_metadata(file_path):
    # Extracting information from the file format
    # Example: C:\Source\clearcouncil\data\PDFs\2020-09-21 County Council - Full Minutes-1952.pdf
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

num_files_to_process = 10  # Set this to the number of files you want to process for testing

# Initialize counter
processed_files = 0

# Using ThreadPoolExecutor for parallel processing
with ThreadPoolExecutor(max_workers=10) as executor:
    # Prepare a list to hold the future tasks
    futures = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf') and len(futures) < num_files_to_process:
            file_path = os.path.join(pdf_dir, filename)
            futures.append(executor.submit(process_pdf, file_path))

    # Process the futures and update the progress bar
    for _ in tqdm(as_completed(futures), total=len(futures), desc="Processing PDFs"):
        pass


# Save the FAISS index to disk
# Format the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d")

# Construct the filename with descriptive information and the current date
index_filename = f"council_meetings_faiss_index_{current_date}.index"

# save indexes to a directory data/faiiss_indexes
save_path = os.path.join('data', 'faiss_indexes')
full_path = os.path.join(save_path, index_filename)

if not os.path.exists(save_path):
    os.makedirs(save_path)

# Save the FAISS index to disk
faiss_store.save(full_path)

            