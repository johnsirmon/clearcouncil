#!/usr/bin/env python3
"""
Test script to extract representative names from PDF documents.
This script attempts to read PDFs with different encoding strategies.
"""

import os
import fitz  # PyMuPDF
import re
from pathlib import Path
import codecs
from typing import List, Set

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def find_representative_names(text: str) -> Set[str]:
    """Extract potential representative names from text."""
    names = set()
    
    # Common patterns for representative mentions
    patterns = [
        r'Council(?:wo)?man\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Representative\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 
        r'District\s+\d+\s*[-–]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'MOVANT:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'SECOND:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Motion\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Seconded\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean up the name
            name = match.strip()
            # Filter out common false positives
            if name and len(name) > 2 and name not in ['Council', 'District', 'Motion', 'Vote']:
                names.add(name)
    
    return names

def analyze_pdfs(pdf_dir: str, max_files: int = 10) -> None:
    """Analyze PDFs in directory to extract representative names."""
    pdf_path = Path(pdf_dir)
    pdf_files = list(pdf_path.glob("*.pdf"))[:max_files]
    
    all_names = set()
    successful_files = 0
    
    print(f"🔍 Analyzing {len(pdf_files)} PDF files for representative names...\n")
    
    for pdf_file in pdf_files:
        print(f"📄 Processing: {pdf_file.name}")
        
        # Try to extract text
        text = extract_text_from_pdf(str(pdf_file))
        
        if text:
            names = find_representative_names(text)
            if names:
                print(f"   ✅ Found names: {', '.join(sorted(names))}")
                all_names.update(names)
                successful_files += 1
            else:
                print(f"   ⚠️  No representative names found")
        else:
            print(f"   ❌ Could not extract text")
        
        print()
    
    print(f"📊 Summary:")
    print(f"   • Files processed: {len(pdf_files)}")
    print(f"   • Files with extracted names: {successful_files}")
    print(f"   • Total unique names found: {len(all_names)}")
    
    if all_names:
        print(f"\n👥 All Representative Names Found:")
        for name in sorted(all_names):
            print(f"   • {name}")
    else:
        print(f"\n⚠️  No representative names could be extracted")

if __name__ == "__main__":
    # Analyze PDFs in the data directory
    pdf_directory = "data/PDFs"
    if os.path.exists(pdf_directory):
        analyze_pdfs(pdf_directory, max_files=20)
    else:
        print(f"❌ PDF directory not found: {pdf_directory}")
