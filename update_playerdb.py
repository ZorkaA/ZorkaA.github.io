import requests as re
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Define the path to the CSV file
csv_file_path = './data/playerdb.csv'


os.makedirs('./data', exist_ok=True)  # Ensures the directory exists


# Load or initialize the DataFrame
if os.path.exists(csv_file_path):
    playerdata = pd.read_csv(csv_file_path)
else:
    playerdata = pd.DataFrame(columns=['Squad'])

print('Obtaining list of squads and their player counts...')
base_url = 'https://stats.warbrokers.io/squads'
page = re.get(base_url)
processed_page = BeautifulSoup(page.text, 'html.parser')

squad_urls = [
    url.replace('/squads/', '') 
    for link in processed_page.find_all('a') 
    if '/squads/' in str(link.get('href'))
    for url in [str(link.get('href'))]
]

squad_urls = tqdm(squad_urls, desc="Processing")

for squad in squad_urls:
    page = re.get(base_url + '/' + squad)
    processed_page = BeautifulSoup(page.text, 'html.parser')
    number_of_players = len([
        link 
        for link in processed_page.find_all('a') 
        if '/players/i/' in str(link.get('href'))
    ])

    # Update the DataFrame
    if squad in playerdata['Squad'].values:
        playerdata.loc[playerdata['Squad'] == squad, datetime.now().strftime('%m/%d/%Y')] = number_of_players
    else:
        row_data = [squad] + [np.nan] * (len(playerdata.columns) - 1)
        new_row = pd.DataFrame([row_data], columns=playerdata.columns)
        playerdata = pd.concat([playerdata, new_row], ignore_index=True)
        playerdata.loc[playerdata['Squad'] == squad, datetime.now().strftime('%m/%d/%Y')] = number_of_players

playerdata.to_csv(csv_file_path, index=False)
