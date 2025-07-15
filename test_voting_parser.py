#!/usr/bin/env python3

import fitz  # PyMuPDF
import sys
import os
import re
from src.clearcouncil.parsers.voting_parser import VotingParser
from src.clearcouncil.config.settings import load_council_config

def test_voting_parser():
    """Test voting parser on a specific PDF"""
    config = load_council_config('york_county_sc')
    parser = VotingParser(config)
    
    pdf_path = "data/PDFs/2019-01-07 County Council - Full Minutes-1802.pdf"
    if os.path.exists(pdf_path):
        # Get the text using PyMuPDF directly
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        
        print("=== Testing individual methods ===")
        lines = text.split('\n')
        
        # Test voting result detection
        voting_result_lines = []
        for i, line in enumerate(lines):
            if parser._is_voting_result_line(line):
                voting_result_lines.append((i, line.strip()))
        
        print(f"Found {len(voting_result_lines)} voting result lines:")
        for i, line in voting_result_lines:
            print(f"\nLine {i}: {line}")
            # Show context around this line
            start = max(0, i-2)
            end = min(len(lines), i+8)
            print("  Context:")
            for j in range(start, end):
                prefix = ">>> " if j == i else "    "
                print(f"{prefix}{j}: {lines[j].strip()}")
            
            if len(voting_result_lines) >= 2:  # Limit output
                break
        
        # Test the full parser
        records = parser.parse_text(text)
        
        print(f"\nFound {len(records)} voting records:")
        for i, record in enumerate(records):
            print(f"\nRecord {i+1}:")
            print(f"  Result: {record.result}")
            print(f"  Movant: {record.movant}")
            print(f"  Representative: {record.representative}")
            print(f"  Second: {record.second}")
            print(f"  Ayes: {record.ayes}")
            print(f"  Case #: {record.case_number}")
            print(f"  Valid: {parser._is_valid_record(record)}")
    else:
        print(f"File not found: {pdf_path}")

if __name__ == "__main__":
    test_voting_parser()
