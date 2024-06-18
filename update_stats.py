import os
from datetime import datetime
import pandas as pd

output_folder = './output'

files = [f for f in os.listdir(output_folder) if f.endswith('apidb.csv')]
dates = [pd.to_datetime(f.split('_')[0], format='%m%d%Y') for f in files]

first_pull = min(dates).strftime('%B %d, %Y') if dates else 'N/A'
last_pull = max(dates).strftime('%B %d, %Y') if dates else 'N/A'
total_pulls = len(files)

print("First Pull:", first_pull)
print("Last Pull:", last_pull)
print("Total Pulls:", total_pulls)

# Write stats to JSON file
with open('stats.json', 'w') as f:
    f.write(f'{{ "firstPull": "{first_pull}", "lastPull": "{last_pull}", "totalPulls": {total_pulls} }}')
