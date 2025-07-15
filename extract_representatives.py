#!/usr/bin/env python3
"""
Extract and clean representative names from York County council documents.
"""

import os
import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import Set, Dict, List
import json

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
        return ""

def clean_representative_names(text: str) -> Set[str]:
    """Extract and clean representative names from council document text."""
    names = set()
    
    # More specific patterns focusing on actual names
    patterns = [
        # Council member followed by first and last name
        r'Council\s+member\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Councilman\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Councilwoman\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        
        # MOVANT and SECOND with first and last names
        r'MOVANT:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'SECOND:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        
        # Motion patterns with full names
        r'Motion\s+by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Seconded\s+by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        
        # Voting patterns (First Last + AYES/NAYS)
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+AYES',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+NAYS',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            name = match.strip()
            
            # Additional cleaning and validation
            if name and len(name.split()) == 2:  # Only first and last name
                first, last = name.split()
                
                # Filter out obvious non-names
                invalid_words = {
                    'PUBLIC', 'HEARING', 'COUNCIL', 'DISTRICT', 'COMMITTEE', 
                    'MOTION', 'VOTE', 'SECOND', 'AYES', 'NAYS', 'MEETING',
                    'CASE', 'NUMBER', 'AND', 'THE', 'FOR', 'TO', 'MADE',
                    'SAID', 'ALSO', 'WILL', 'WOULD', 'LIKE', 'THAT', 'WERE',
                    'UNABLE', 'AGREED', 'REQUESTED', 'INDICATED', 'EXPRESSED',
                    'RECOGNIZED', 'PROVIDED', 'TOLD', 'WISHED', 'EVERYONE',
                    'DESIGNATED', 'ELECTED', 'NOMINATED', 'ACCEPTED',
                    'ADJOURNMENT', 'COMMENTS', 'BUSINESS', 'RECOMMENDATIONS',
                    'LIMITS', 'VACANT', 'NEW', 'OTHER', 'FINANCE', 'RECEIVE',
                    'BOARD', 'CONDITIONS', 'RESOLUTION', 'OWN', 'AT', 'PADDLER'
                }
                
                if (first.upper() not in invalid_words and 
                    last.upper() not in invalid_words and
                    len(first) > 1 and len(last) > 1 and
                    first.isalpha() and last.isalpha()):
                    names.add(f"{first} {last}")
    
    return names

def get_all_representatives(pdf_dir: str, max_files: int = None) -> Dict:
    """Get comprehensive list of representatives from all PDF files."""
    pdf_path = Path(pdf_dir)
    pdf_files = list(pdf_path.glob("*.pdf"))
    
    if max_files:
        pdf_files = pdf_files[:max_files]
    
    all_names = set()
    files_with_names = []
    
    print(f"🔍 Analyzing {len(pdf_files)} PDF files for representatives...")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        if i % 50 == 0:
            print(f"   Processed {i}/{len(pdf_files)} files...")
        
        text = extract_text_from_pdf(str(pdf_file))
        if text:
            names = clean_representative_names(text)
            if names:
                all_names.update(names)
                files_with_names.append({
                    'file': pdf_file.name,
                    'names': list(names)
                })
    
    # Sort names and create final list
    sorted_names = sorted(all_names)
    
    result = {
        'total_files_processed': len(pdf_files),
        'files_with_representatives': len(files_with_names),
        'total_unique_names': len(sorted_names),
        'representatives': sorted_names,
        'sample_files': files_with_names[:10]  # Sample of files for verification
    }
    
    return result

def save_representatives_list(data: Dict, output_file: str) -> None:
    """Save representatives data to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"💾 Saved representatives data to {output_file}")

if __name__ == "__main__":
    # Analyze all PDFs
    pdf_directory = "data/PDFs"
    output_file = "data/representatives.json"
    
    if os.path.exists(pdf_directory):
        print("🏛️  York County Council Representatives Extraction")
        print("=" * 50)
        
        # Get all representatives
        data = get_all_representatives(pdf_directory)
        
        # Display results
        print(f"\n📊 Results:")
        print(f"   • Total PDF files processed: {data['total_files_processed']}")
        print(f"   • Files containing representative names: {data['files_with_representatives']}")
        print(f"   • Total unique representatives found: {data['total_unique_names']}")
        
        print(f"\n👥 York County Council Representatives:")
        for i, name in enumerate(data['representatives'], 1):
            print(f"   {i:2d}. {name}")
        
        # Save to file
        save_representatives_list(data, output_file)
        
        print(f"\n💡 Use this data to:")
        print(f"   • Track individual representative voting patterns")
        print(f"   • Analyze representative activity over time")
        print(f"   • Generate representative-specific reports")
        
    else:
        print(f"❌ PDF directory not found: {pdf_directory}")
