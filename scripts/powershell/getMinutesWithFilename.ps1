# Define the base URL
$baseUrl = "https://yorkcountysc.iqm2.com/Citizens/FileOpen.aspx?Type=12&ID="

# Create the directory if it doesn't exist
$savePath = "C:\Source\clearcouncil\data\PDFs"
if (-not (Test-Path $savePath)) {
    New-Item -ItemType Directory -Path $savePath
}

# Loop through the IDs from 1800 to 2000
for ($id = 1800; $id -le 1803; $id++) {
    $fullUrl = $baseUrl + $id + "&Inline=True"

    # Try to download the file
    try {
        # Request the file
        $response = Invoke-WebRequest -Uri $fullUrl -Method Head

        # Extract the filename from the Content-Disposition header
        $contentDisposition = $response.Headers["Content-Disposition"]
        if ($contentDisposition -and $contentDisposition -match 'filename="(.+)"') {
            $fileName = $matches[1]
        } else {
            $fileName = "file_$id.pdf"
        }

        $localFile = Join-Path $savePath $fileName

        # Download the file
        Invoke-WebRequest -Uri $fullUrl -OutFile $localFile
        Write-Host "Downloaded file $localFile"
    } catch {
        Write-Host "No file found for ID $id"
    }
}
