import requests
import csv
import os
from datetime import datetime
from tqdm import tqdm

# CSV file location
csv_file_path = 'data/wbuserdata.csv'  # Adjusted for GitHub Pages directory

# Mapping for human-readable names for damage dealt
damage_names = {
    'p11': 'BGM',
    'p52': 'DamageDealt_p52',
    'p53': 'DamageDealt_p53',
    'p54': 'DamageDealt_p54',
    'p55': 'DamageDealt_p55',
    'p56': 'DamageDealt_p56',
    'p57': 'DamageDealt_p57',
    'p58': 'DamageDealt_p58',
    'p59': 'DamageDealt_p59',
    'p60': 'DamageDealt_p60',
    'p61': 'AR',
    'p62': 'AK',
    'p63': 'Pistol',
    'p64': 'HR',
    'p65': 'RPG',
    'p66': 'Shotgun',
    'p67': 'SR',
    'p68': 'SMG',
    'p69': 'Homing',
    'p71': 'Grenade',
    'p74': 'HeliMinigun',
    'p75': 'TankMinigun',
    'p76': 'Knife',
    'p78': 'Revolver',
    'p79': 'Minigun',
    'p80': 'GL',
    'p82': 'DamageDealt_p82',
    'p83': 'DamageDealt_p83',
    'p84': 'DamageDealt_p84',
    'p85': 'DamageDealt_p85',
    'p86': 'DamageDealt_p86',
    'p87': 'DamageDealt_p87',
    'p88': 'Fists',
    'p89': 'VSS',
    'p90': 'Fifty',
    'p91': 'MGTurret',
    'p92': 'XBow',
    'p93': 'SCAR',
    'p94': 'TacShotty',
    'p95': 'VEK',
    'p96': 'DamageDealt_p96',
    'p97': 'DamageDealt_p97',
    'p98': 'LMG',
    'p101': 'DamageDealt_p101',
    'p104': 'DamageDealt_p104',
    'p105': 'DamageDealt_p105',
    'p110': 'DamageDealt_p110',
    'p111': 'LaserMine',
    'p112': 'DamageDealt_p112'
}

# API URLs
squad_list_url = "https://wbapi.wbpjs.com/squad/getSquadList"
squad_members_url = "https://wbapi.wbpjs.com/squad/getSquadMembers?squadName={}"
player_info_url = "https://wbapi.wbpjs.com/players/getPlayer?uid={}"

# Get the current date
today = datetime.today().strftime('%d%m%Y')

# Function to get squad list
def get_squad_list():
    response = requests.get(squad_list_url)
    return response.json()

# Function to get squad members
def get_squad_members(squad_name):
    response = requests.get(squad_members_url.format(squad_name))
    return response.json()

# Function to get player info
def get_player_info(uid):
    response = requests.get(player_info_url.format(uid))
    return response.json()

# Function to map damage dealt to human-readable names
def map_damage_dealt(damage_dealt):
    return {damage_names.get(k, k): v for k, v in damage_dealt.items()}

# Check if CSV exists and get headers if it does
if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader, None)
else:
    headers = None

# If the CSV is new, write headers
if not headers:
    headers = ['Date', 'Squad', 'Name', 'Level', 'XP', 'JoinTime', 'PingTime', 'Banned', 'Coins', 'KillsELO', 'GamesELO', 'Number_of_Jumps', 'Zombie_Deaths', 'Zombie_Kills', 'Zombie_Wins', 'Time', 'Time_Alive_Count', 'Time_Alive_Longest', 'Time_Alive', 'Zombie_Time_Alive_Count', 'Zombie_Time_Alive'] + list(damage_names.values()) + [f"Losses_{key}" for key in ['m00', 'm10', 'm09', 'm08', 'm07']]
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

# Get the list of squads
squads = get_squad_list()

# Calculate total number of players for the progress bar
total_players = sum(len(get_squad_members(squad)) for squad in squads)

# Create a single progress bar for all players
with tqdm(total=total_players, desc="Processing Players", unit="player") as progress_bar:
    for squad in squads:
        members = get_squad_members(squad)

        for member in members:
            player_info = get_player_info(member['uid'])

            # Skip if player_info is None
            if not player_info:
                continue

            # Ensure player_info['losses'] is a dictionary
            losses = player_info.get('losses') if isinstance(player_info.get('losses'), dict) else {}

            damage_dealt = map_damage_dealt(player_info.get('damage_dealt', {}))

            # Create a row with all relevant player info
            row = [
                today,
                squad,
                player_info.get('nick'),
                player_info.get('level'),
                player_info.get('xp'),
                player_info.get('joinTime'),
                player_info.get('ping_time'),
                player_info.get('banned'),
                player_info.get('coins'),
                player_info.get('killsELO'),
                player_info.get('gamesELO'),
                player_info.get('number_of_jumps'),
                player_info.get('zombie_deaths'),
                player_info.get('zombie_kills'),
                player_info.get('zombie_wins'),
                player_info.get('time'),
                player_info.get('time_alive_count'),
                player_info.get('time_alive_longest'),
                player_info.get('time_alive'),
                player_info.get('zombie_time_alive_count'),
                player_info.get('zombie_time_alive')
            ] + [damage_dealt.get(name, 0) for name in damage_names.values()] + [losses.get(key, 0) for key in ['m00', 'm10', 'm09', 'm08', 'm07']]

            # Open the CSV file to append data
            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)

            # Update the progress bar
            progress_bar.update(1)
