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
# This section will be used to create the embeddings for the text
# We will be using the OpenAIEmbeddings class to create the embeddings
# The OpenAIEmbeddings class takes in the OpenAI API key as the parameter
# The OpenAIEmbeddings class has a method called create_embeddings
# this will loop through the pdf files in the data folder for PDFs first and then
# create the embeddings for each of the PDFs and store them in the embeddings folder
# The embeddings folder will be created if it doesn't exist
# The embeddings will be stored in a file called embeddings.faiss
# The embeddings will be stored in the FAISS format
# The FAISS format is a binary format that is used to store the embeddings

# Create the embeddings
embeddings = OpenAIEmbeddings(os.getenv("OPENAI_API_KEY"))
embeddings.create_embeddings(
    "data/pdf",
    "embeddings", 
    "embeddings.faiss" 
)

# This section will be used to create the text splitter
# We will be using the CharacterTextSplitter class to create the text splitter
# The CharacterTextSplitter class takes in the embeddings file as the parameter
# The CharacterTextSplitter class has a method called create_text_splitter
# this will create the text splitter and store it in the text_splitter folder
# The text_splitter folder will be created if it doesn't exist
# The text splitter will be stored in a file called text_splitter.pickle
# The text splitter will be stored in the pickle format
# The pickle format is a binary format that is used to store the text splitter

# Create the text splitter
text_splitter = CharacterTextSplitter("embeddings/embeddings.faiss")
text_splitter.create_text_splitter("text_splitter", "text_splitter.pickle")

# This section will be used to create the vector store
# We will be using the FAISS class to create the vector store
# The FAISS class takes in the embeddings file as the parameter
# The FAISS class has a method called create_vector_store
# this will create the vector store and store it in the vector_store folder
# The vector_store folder will be created if it doesn't exist
# The vector store will be stored in a file called vector_store.faiss
# The vector store will be stored in the FAISS format
# The FAISS format is a binary format that is used to store the vector store

# Create the vector store
vector_store = FAISS("embeddings/embeddings.faiss")
vector_store.create_vector_store("vector_store", "vector_store.faiss")






