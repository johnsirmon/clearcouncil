# Define the base URL
$baseUrl = "https://yorkcountysc.iqm2.com/Citizens/FileOpen.aspx?Type=12&ID="

# Create the directory if it doesn't exist
$savePath = "C:\johnsi1\YorkCounty"
if (-not (Test-Path $savePath)) {
    New-Item -ItemType Directory -Path $savePath
}

# Loop through the IDs from 1895 to 1896
for ($id = 1895; $id -le 1973; $id++) {
    $fullUrl = $baseUrl + $id + "&Inline=True"
    $localFile = Join-Path $savePath "2020_$id.pdf"

    # Try to download the file
    try {
        Invoke-WebRequest -Uri $fullUrl -OutFile $localFile
        Write-Host "Downloaded file $id"
    } catch {
        Write-Host "No file found for ID $id"
    }
}
