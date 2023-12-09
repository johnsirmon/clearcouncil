import requests

# Define the base URL
base_url = "https://yorkcountysc.iqm2.com/Citizens/FileOpen.aspx?Type=12&ID="

# Define the range of Meeting IDs to download (2168 to 2199)
start_id = 2168
end_id = 2199

# Iterate through the range of Meeting IDs
for meeting_id in range(start_id, end_id + 1):
    # Construct the URL for the current Meeting ID
    pdf_url = f"{base_url}{meeting_id}&Inline=True"

    # Send a request to download the PDF
    response = requests.get(pdf_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the PDF file with a default filename
        with open(f"Meeting_ID_{meeting_id}.pdf", "wb") as file:
            file.write(response.content)

        print(f"Downloaded Meeting ID {meeting_id}")
    else:
        print(f"Failed to download Meeting ID {meeting_id}")

print("Download completed.")
