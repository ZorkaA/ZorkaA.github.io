import os
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Define the Google Drive folder ID and your credentials file
folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
credentials = service_account.Credentials.from_service_account_file(
    'path/to/your/credentials.json')

service = build('drive', 'v3', credentials=credentials)

# List files in the Google Drive folder
results = service.files().list(
    q=f"'{folder_id}' in parents and mimeType='text/csv'",
    spaces='drive',
    fields='files(name, id)').execute()
files = results.get('files', [])

# Filter files and extract dates
csv_files = [f for f in files if f['name'].endswith('_apidb.csv')]
dates = [datetime.strptime(f['name'].split('_')[0], '%m%d%Y') for f in csv_files]

# Calculate stats
first_pull = min(dates).strftime('%B %d, %Y') if dates else 'N/A'
last_pull = max(dates).strftime('%B %d, %Y') if dates else 'N/A'
total_pulls = len(csv_files)

# Update HTML file
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Stats</title>
</head>
<body>
    <h1>Data Pull Statistics</h1>
    <p>First Pull  : {first_pull}</p>
    <p>Last Pull   : {last_pull}</p>
    <p>Total Pulls : {total_pulls}</p>
</body>
</html>
"""

with open('index.html', 'w') as f:
    f.write(html_content)
