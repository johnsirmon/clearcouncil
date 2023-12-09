#!/bin/bash

# Define the base URL
baseUrl="https://yorkcountysc.iqm2.com/Citizens/FileOpen.aspx?Type=12&ID="

# Create the directory if it doesn't exist
savePath="/c/Source/clearcouncil/data/PDFs"
mkdir -p "$savePath" || { echo "Failed to create directory $savePath"; exit 1; }

# Loop through the IDs from 1800 (around 2018) to 2256 (around 2023)
for id in {2004..2256}; do
    fullUrl="${baseUrl}${id}&Inline=True"

    # Try to get the filename from the Content-Disposition header using curl
    contentDisposition=$(curl -sI "$fullUrl" | grep -o -E 'filename="[^"]+')
    if [[ $contentDisposition ]]; then
        fileName=$(echo $contentDisposition | sed 's/filename="//;s/"$//')
    else
        fileName="file_$id.pdf"
    fi

    localFile="${savePath}/${fileName}"

    # Download the file using curl
    curl -s -o "$localFile" "$fullUrl" && echo "Downloaded file $localFile" || { echo "Failed to download file for ID $id"; exit 1; }
done
