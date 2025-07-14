"""Configuration management for different councils."""

import os
import yaml
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class WebsiteConfig:
    """Website configuration for document downloading."""
    base_url: str
    document_url_template: str
    id_ranges: List[Dict[str, Any]]


@dataclass
class FilePatterns:
    """File naming and pattern configurations."""
    pdf_pattern: str
    date_format: str


@dataclass
class StorageConfig:
    """Data storage directory configurations."""
    pdf_directory: str
    transcript_directory: str
    index_directory: str
    results_directory: str


@dataclass
class ProcessingConfig:
    """Processing configuration parameters."""
    chunk_size: int
    max_workers: int
    embedding_model: str


@dataclass
class YouTubeConfig:
    """YouTube transcript configuration."""
    default_video_ids: List[str]


@dataclass
class ParsingConfig:
    """Document parsing configuration."""
    voting_fields: List[str]


@dataclass
class CouncilConfig:
    """Complete configuration for a council."""
    name: str
    identifier: str
    description: str
    website: WebsiteConfig
    file_patterns: FilePatterns
    storage: StorageConfig
    processing: ProcessingConfig
    youtube: YouTubeConfig
    parsing: ParsingConfig

    def get_data_path(self, data_type: str) -> Path:
        """Get the full path for a data directory."""
        base_path = Path.cwd()
        
        if data_type == "pdf":
            return base_path / self.storage.pdf_directory
        elif data_type == "transcript":
            return base_path / self.storage.transcript_directory
        elif data_type == "index":
            return base_path / self.storage.index_directory
        elif data_type == "results":
            return base_path / self.storage.results_directory
        else:
            raise ValueError(f"Unknown data type: {data_type}")

    def ensure_directories(self):
        """Create all necessary directories if they don't exist."""
        for data_type in ["pdf", "transcript", "index", "results"]:
            path = self.get_data_path(data_type)
            path.mkdir(parents=True, exist_ok=True)


def load_council_config(council_id: str) -> CouncilConfig:
    """Load configuration for a specific council."""
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "councils" / f"{council_id}.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Council configuration not found: {config_path}")
    
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    
    return CouncilConfig(
        name=data["name"],
        identifier=data["identifier"],
        description=data["description"],
        website=WebsiteConfig(**data["website"]),
        file_patterns=FilePatterns(**data["file_patterns"]),
        storage=StorageConfig(**data["storage"]),
        processing=ProcessingConfig(**data["processing"]),
        youtube=YouTubeConfig(**data["youtube"]),
        parsing=ParsingConfig(**data["parsing"])
    )


def list_available_councils() -> List[str]:
    """List all available council configurations."""
    config_dir = Path(__file__).parent.parent.parent.parent / "config" / "councils"
    council_files = config_dir.glob("*.yaml")
    
    councils = []
    for file_path in council_files:
        if file_path.name != "template.yaml":
            councils.append(file_path.stem)
    
    return councils