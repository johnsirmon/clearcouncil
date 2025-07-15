#!/usr/bin/env python3

import fitz  # PyMuPDF
import sys
import os

def extract_pdf_text(pdf_path):
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""

if __name__ == "__main__":
    pdf_path = "data/PDFs/2019-01-07 County Council - Full Minutes-1802.pdf"
    if os.path.exists(pdf_path):
        text = extract_pdf_text(pdf_path)
        print(f"=== Text from {pdf_path} ===")
        print(text[:3000])  # First 3000 chars
        print("\n=== Looking for voting patterns ===")
        lines = text.split('\n')
        voting_lines = []
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ['vote', 'motion', 'second', 'aye', 'nay', 'abstain']):
                voting_lines.append(f"Line {i}: {line.strip()}")
        
        for line in voting_lines[:20]:  # Show first 20 voting-related lines
            print(line)
    else:
        print(f"File not found: {pdf_path}")
