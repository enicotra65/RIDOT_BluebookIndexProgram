import os
import requests
from urllib.parse import urlparse
import re
import json

"""
This python file will download the files of the links provided, 
In this case the Bluebook Archives on the RIDOT Website, and will
save them to a folder in the directory it resides in, and will also
rename the files to "YYYY_MM" format. To be distinguished by the other
pages. This page is made to only to fetch the PDF files for further 
processing.
"""

# Function to download PDF from a URL
def download_pdf(url):
    # Send a GET request to the URL
    response = requests.get(url)
    if response.status_code == 200:  # Check if the request was successful
        # Extract the filename from the URL
        filename = os.path.basename(urlparse(url).path)
        # Get the publication year and month from the filename
        year, month = get_year_and_month(filename)
        if year and month:  # Check if year and month were successfully extracted
            # Create the new filename in the format YYYY_MM
            new_filename = f"{year}_{month}"
            # Save the PDF content to a file with the new filename
            with open(f"bluebook_pdfs/{new_filename}.pdf", "wb") as file:
                file.write(response.content)
            print(f"Downloaded Bluebook: {new_filename}.pdf")
        else:
            print(f"Failed to extract year and month from filename: {filename}")
    else:
        print(f"Failed to download Bluebook from URL: {url}")


# Function to extract year and month from a filename
def get_year_and_month(filename):
    # Remove the file extension from the filename
    filename = os.path.splitext(filename)[0]
    # Regular expression to find MM and YYYY or MM and YY patterns
    match = re.search(r'(\d{2})[_-](\d{4})', filename)  # Match MM_YYYY or MM-YYYY
    if match:
        return match.group(2), match.group(1)
    match = re.search(r'(\d{2})[_-](\d{2})', filename)  # Match MM_YY or MM-YY
    if match:
        return "20" + match.group(2), match.group(1)
    return None, None  # Return None if year and month could not be extracted

# Load PDF URLs from JSON file
with open("pdf_urls.json", "r") as file:
    data = json.load(file)
pdf_urls = data["urls"]

# Create a directory to store the downloaded PDFs if it doesn't exist
if not os.path.exists("bluebook_pdfs"):
    os.makedirs("bluebook_pdfs")

# Loop through each URL in the list and download the PDF
for pdf_url in pdf_urls:
    download_pdf(pdf_url)
