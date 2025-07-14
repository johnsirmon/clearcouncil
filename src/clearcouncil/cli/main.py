"""Main CLI interface for ClearCouncil."""

import argparse
import asyncio
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from tqdm import tqdm

from ..config.settings import CouncilConfig, load_council_config, list_available_councils
from ..core.database import VectorDatabase
from ..core.exceptions import ClearCouncilError
from ..processors.pdf_processor import PDFProcessor
from ..processors.transcript_processor import TranscriptProcessor
from ..downloaders.pdf_downloader import PDFDownloader
from ..parsers.voting_parser import VotingParser
from .voting_commands import add_voting_analysis_commands


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('clearcouncil.log')
        ]
    )


def ensure_environment():
    """Ensure required environment variables are set."""
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please create a .env file with your OpenAI API key")
        sys.exit(1)


def process_pdfs_command(args):
    """Process PDF files and create vector embeddings."""
    config = load_council_config(args.council)
    config.ensure_directories()
    
    # Initialize components
    processor = PDFProcessor(config)
    database = VectorDatabase(config)
    
    # Get PDF files to process
    pdf_dir = config.get_data_path("pdf")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return
    
    print(f"Processing {len(pdf_files)} PDF files...")
    
    # Process files with threading
    processed_count = 0
    with ThreadPoolExecutor(max_workers=config.processing.max_workers) as executor:
        # Submit all tasks
        futures = [
            executor.submit(processor.process_with_result, pdf_file) 
            for pdf_file in pdf_files
        ]
        
        # Process results as they complete
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing PDFs"):
            result = future.result()
            
            if result.success:
                database.add_document(result.document)
                processed_count += 1
            else:
                print(f"Error: {result.error}")
    
    # Save the vector database
    index_path = database.save_index()
    print(f"Successfully processed {processed_count}/{len(pdf_files)} files")
    print(f"Vector index saved to: {index_path}")


def download_pdfs_command(args):
    """Download PDF documents from council website."""
    config = load_council_config(args.council)
    config.ensure_directories()
    
    downloader = PDFDownloader(config)
    
    # Test connection first
    if not downloader.test_connection():
        print("Warning: Could not connect to council website")
    
    try:
        if args.document_id:
            # Download single document
            file_path = downloader.download_document(args.document_id)
            print(f"Downloaded: {file_path}")
        else:
            # Download range from config
            range_index = args.range_index or 0
            files = downloader.download_from_config(range_index)
            print(f"Downloaded {len(files)} files")
            
    except ClearCouncilError as e:
        print(f"Download failed: {e}")
        sys.exit(1)


def process_transcripts_command(args):
    """Process YouTube transcripts."""
    config = load_council_config(args.council)
    config.ensure_directories()
    
    processor = TranscriptProcessor(config)
    database = VectorDatabase(config)
    
    if args.video_id:
        # Process single video
        try:
            document = processor.process_video_id(args.video_id)
            database.add_document(document)
            print(f"Processed transcript for video: {args.video_id}")
        except ClearCouncilError as e:
            print(f"Failed to process transcript: {e}")
            sys.exit(1)
    else:
        print("Video ID is required for transcript processing")
        sys.exit(1)


def parse_voting_command(args):
    """Parse voting records from documents."""
    config = load_council_config(args.council)
    parser = VotingParser(config)
    
    if args.file_path:
        # Parse single file
        try:
            records = parser.parse_file(args.file_path)
            output_path = config.get_data_path("results") / "voting_records.csv"
            parser.save_to_csv(records, output_path)
            print(f"Extracted {len(records)} voting records to {output_path}")
        except ClearCouncilError as e:
            print(f"Parsing failed: {e}")
            sys.exit(1)
    else:
        print("File path is required for voting record parsing")
        sys.exit(1)


def search_command(args):
    """Search the vector database."""
    config = load_council_config(args.council)
    database = VectorDatabase(config)
    
    try:
        results = database.search(args.query, k=args.limit)
        
        print(f"Found {len(results)} results for: '{args.query}'\\n")
        
        for i, result in enumerate(results, 1):
            print(f"Result {i} (Score: {result['score']:.3f}):")
            print(f"Content: {result['content'][:200]}...")
            if result['metadata']:
                print(f"Metadata: {result['metadata']}")
            print("-" * 50)
            
    except ClearCouncilError as e:
        print(f"Search failed: {e}")
        sys.exit(1)


def list_councils_command(args):
    """List available councils."""
    councils = list_available_councils()
    
    print("Available councils:")
    for council_id in councils:
        try:
            config = load_council_config(council_id)
            print(f"  {council_id}: {config.name}")
        except Exception:
            print(f"  {council_id}: (configuration error)")


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="ClearCouncil - Local Government Transparency Tool"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List councils command
    list_parser = subparsers.add_parser("list-councils", help="List available councils")
    
    # Process PDFs command
    process_parser = subparsers.add_parser("process-pdfs", help="Process PDF files")
    process_parser.add_argument("council", help="Council identifier")
    
    # Download PDFs command
    download_parser = subparsers.add_parser("download-pdfs", help="Download PDF documents")
    download_parser.add_argument("council", help="Council identifier")
    download_parser.add_argument("--document-id", help="Download specific document ID")
    download_parser.add_argument("--range-index", type=int, help="Use specific ID range from config")
    
    # Process transcripts command
    transcript_parser = subparsers.add_parser("process-transcripts", help="Process YouTube transcripts")
    transcript_parser.add_argument("council", help="Council identifier")
    transcript_parser.add_argument("--video-id", required=True, help="YouTube video ID")
    
    # Parse voting records command
    voting_parser = subparsers.add_parser("parse-voting", help="Parse voting records")
    voting_parser.add_argument("council", help="Council identifier")
    voting_parser.add_argument("--file-path", required=True, help="Path to document file")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search documents")
    search_parser.add_argument("council", help="Council identifier")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=5, help="Number of results to return")
    
    # Add voting analysis commands
    add_voting_analysis_commands(subparsers)
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    ensure_environment()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "list-councils":
            list_councils_command(args)
        elif args.command == "process-pdfs":
            process_pdfs_command(args)
        elif args.command == "download-pdfs":
            download_pdfs_command(args)
        elif args.command == "process-transcripts":
            process_transcripts_command(args)
        elif args.command == "parse-voting":
            parse_voting_command(args)
        elif args.command == "search":
            search_command(args)
        elif args.command in ["analyze-voting", "analyze-district", "update-documents", "explain-terms"]:
            # Handle async voting analysis commands
            if hasattr(args, 'func'):
                if asyncio.iscoroutinefunction(args.func):
                    asyncio.run(args.func(args))
                else:
                    args.func(args)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\\nOperation cancelled by user")
        sys.exit(1)
    except ClearCouncilError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.exception("Unexpected error occurred")
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()