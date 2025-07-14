"""Vector database interface for document embeddings."""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import logging

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter

from .models import Document, DocumentMetadata
from .exceptions import DatabaseError
from ..config.settings import CouncilConfig

logger = logging.getLogger(__name__)


class VectorDatabase:
    """Manages FAISS vector database for document embeddings."""
    
    def __init__(self, config: CouncilConfig):
        """Initialize the vector database."""
        self.config = config
        self.embeddings = OpenAIEmbeddings(model=config.processing.embedding_model)
        self.text_splitter = CharacterTextSplitter(
            chunk_size=config.processing.chunk_size
        )
        self._store: Optional[FAISS] = None
        
    def _ensure_store_initialized(self):
        """Ensure the FAISS store is initialized."""
        if self._store is None:
            try:
                # Try to load existing index
                index_path = self._get_latest_index_path()
                if index_path and index_path.exists():
                    self._store = FAISS.load_local(str(index_path), self.embeddings)
                    logger.info(f"Loaded existing FAISS index from {index_path}")
                else:
                    # Create new empty store
                    self._store = FAISS.from_texts(
                        ["Initial document"], 
                        self.embeddings,
                        metadatas=[{"type": "initial"}]
                    )
                    logger.info("Created new FAISS index")
            except Exception as e:
                raise DatabaseError(f"Failed to initialize vector store: {e}")
    
    def add_document(self, document: Document) -> None:
        """Add a document to the vector database."""
        self._ensure_store_initialized()
        
        try:
            # Split document into chunks if not already done
            if not document.chunks:
                document.chunks = self.text_splitter.split_text(document.content)
            
            # Create metadata for each chunk
            chunk_metadatas = []
            for i, chunk in enumerate(document.chunks):
                metadata = document.metadata.to_dict()
                metadata['chunk_index'] = i
                metadata['chunk_count'] = len(document.chunks)
                chunk_metadatas.append(metadata)
            
            # Add to FAISS store
            self._store.add_texts(document.chunks, metadatas=chunk_metadatas)
            logger.info(f"Added document with {len(document.chunks)} chunks to vector database")
            
        except Exception as e:
            raise DatabaseError(f"Failed to add document to vector database: {e}")
    
    def save_index(self, custom_name: Optional[str] = None) -> Path:
        """Save the current FAISS index to disk."""
        if self._store is None:
            raise DatabaseError("No vector store to save")
        
        try:
            # Generate filename
            if custom_name:
                filename = custom_name
            else:
                current_date = datetime.now().strftime("%Y%m%d")
                filename = f"council_meetings_faiss_index_{current_date}"
            
            # Ensure index directory exists
            index_dir = self.config.get_data_path("index")
            index_dir.mkdir(parents=True, exist_ok=True)
            
            # Save index
            index_path = index_dir / filename
            self._store.save_local(str(index_path))
            logger.info(f"Saved FAISS index to {index_path}")
            
            return index_path
            
        except Exception as e:
            raise DatabaseError(f"Failed to save FAISS index: {e}")
    
    def _get_latest_index_path(self) -> Optional[Path]:
        """Get the path to the most recent FAISS index."""
        index_dir = self.config.get_data_path("index")
        if not index_dir.exists():
            return None
        
        # Look for index files
        index_files = list(index_dir.glob("council_meetings_faiss_index_*"))
        if not index_files:
            return None
        
        # Return the most recent one (by filename which includes date)
        return max(index_files, key=lambda x: x.name)
    
    def search(self, query: str, k: int = 5) -> List[dict]:
        """Search the vector database for similar documents."""
        self._ensure_store_initialized()
        
        try:
            results = self._store.similarity_search_with_score(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to search vector database: {e}")
    
    def get_document_count(self) -> int:
        """Get the number of documents in the database."""
        if self._store is None:
            return 0
        return self._store.index.ntotal if hasattr(self._store, 'index') else 0