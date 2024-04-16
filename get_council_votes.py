import pandas as pd
import PyPDF2

def extract_information_from_pdf(file_path):
    # Open the PDF file
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        # Extract text from each page
        for page in reader.pages:
            text += page.extract_text()

    return text

def parse_data(text):
    # Split the text into lines
    lines = text.split('\n')

    # Prepare a list to store each entry
    data = []

def parse_data(text):
    lines = text.split('\n')
    data = []

    # Temporary dictionary to hold the extracted details
    rezoning_details = {}

    for line in lines:
        if 'Council District:' in line:
            district_part = line.split('Council District:')[1].strip().split('-')
            rezoning_details['District'] = district_part[0].strip()
            rezoning_details['Representative'] = district_part[1].strip()
        elif 'Case #' in line:
            rezoning_details['Case Number'] = line.split('Case #')[1].strip()
        elif 'Acres:' in line:
            rezoning_details['Acres'] = line.split('Acres:')[1].strip()
        elif 'Owner:' in line:
            rezoning_details['Owner'] = line.split('Owner:')[1].strip()
        elif 'Location:' in line:
            rezoning_details['Location'] = line.split('Location:')[1].strip()
        elif 'Applicant:' in line:
            rezoning_details['Applicant'] = line.split('Applicant:')[1].strip()
        elif 'Planning Commission Date:' in line:
            rezoning_details['Planning Commission Date'] = line.split('Planning Commission Date:')[1].strip()
        elif 'Staff Recommendation:' in line:
            rezoning_details['Staff Recommendation'] = line.split('Staff Recommendation:')[1].strip()
        elif 'PC Recommendation:' in line:
            rezoning_details['PC Recommendation'] = line.split('PC Recommendation:')[1].strip()
        elif 'Zoning Request:' in line:
            rezoning_details['Zoning Request'] = line.split('Zoning Request:')[1].strip()
        elif 'Rezoning Action:' in line:
            rezoning_details['Rezoning Action'] = line.split('Rezoning Action:')[1].strip()
        elif 'MOVANT:' in line:
            movant_parts = line.split('MOVANT:')
            rezoning_details['Movant'] = movant_parts[1].split('SECOND:')[0].strip() if len(movant_parts) > 1 else None

            second_parts = line.split('SECOND:')
            rezoning_details['Second'] = second_parts[1].strip() if len(second_parts) > 1 else None

            # Append the collected details to the data list and reset for next entry
            data.append(rezoning_details.copy())
            rezoning_details.clear()  # Reset for the next entry

    return data



def save_to_csv(data, filename='results.csv'):
    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(data)
    # Save DataFrame to CSV
    df.to_csv(filename, index=False)

# Usage
pdf_text = extract_information_from_pdf(r'C:\Users\johnsirmon\Downloads\2024-04-01 County Council - Full Minutes-2283 (2).pdf')
parsed_data = parse_data(pdf_text)
save_to_csv(parsed_data)
