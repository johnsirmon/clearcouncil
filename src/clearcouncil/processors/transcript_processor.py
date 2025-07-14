"""YouTube transcript processor."""

import os
from pathlib import Path
from typing import Optional
import logging

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from .base_processor import BaseProcessor
from ..core.models import Document, DocumentMetadata
from ..core.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class TranscriptProcessor(BaseProcessor):
    """Processes YouTube transcripts for council meetings."""
    
    def __init__(self, config):
        """Initialize transcript processor."""
        super().__init__(config)
        self.formatter = TextFormatter()
    
    def download_transcript(self, video_id: str, save_directory: Optional[Path] = None) -> Path:
        """Download transcript for a YouTube video and save to file."""
        try:
            # Get transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Format as text
            formatted_transcript = "\n".join([entry['text'] for entry in transcript])
            
            # Determine save path
            if save_directory is None:
                save_directory = self.config.get_data_path("transcript")
            
            save_directory.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            file_path = save_directory / f"{video_id}_transcript.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_transcript)
            
            logger.info(f"Downloaded transcript for video {video_id} to {file_path}")
            return file_path
            
        except Exception as e:
            raise ProcessingError(f"Failed to download transcript for video {video_id}: {e}")
    
    def process_file(self, file_path: Path) -> Document:
        """Process a transcript file and return a Document object."""
        self.validate_file(file_path)
        
        try:
            # Read transcript content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract video ID from filename
            video_id = self._extract_video_id_from_filename(file_path)
            
            # Create metadata
            metadata = DocumentMetadata(
                file_path=file_path,
                council_id=self.config.identifier,
                document_type="transcript",
                document_id=video_id
            )
            
            # Split into chunks (transcripts can be long)
            chunks = self._split_transcript(content)
            
            return Document(
                content=content,
                metadata=metadata,
                chunks=chunks
            )
            
        except Exception as e:
            raise ProcessingError(f"Failed to process transcript {file_path}: {e}")
    
    def _extract_video_id_from_filename(self, file_path: Path) -> Optional[str]:
        """Extract video ID from transcript filename."""
        filename = file_path.stem
        if filename.endswith('_transcript'):
            return filename.replace('_transcript', '')
        return filename
    
    def _split_transcript(self, content: str) -> list:
        """Split transcript into meaningful chunks."""
        # Split by paragraphs or sentences for better semantic chunks
        paragraphs = content.split('\n\n')
        
        chunks = []
        current_chunk = ""
        max_chunk_size = self.config.processing.chunk_size
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [content]
    
    def process_video_id(self, video_id: str) -> Document:
        """Download and process a transcript by video ID."""
        file_path = self.download_transcript(video_id)
        return self.process_file(file_path)
    
    def get_supported_extensions(self) -> list:
        """Get list of supported file extensions."""
        return ['.txt']