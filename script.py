import requests
import csv
import os
from datetime import datetime
from tqdm import tqdm

# CSV file location
csv_file_path = 'data/wbuserdata.csv'  # Adjusted for GitHub Pages directory

# Mapping for human-readable names for damage dealt
damage_names = {
    'p09': 'AirStrike',
    'p11': 'BGM',
    'p52': 'TankLvl1',
    'p53': 'APCLvl1',
    'p54': 'HeliLvl1',
    'p55': 'TankLvl2',
    'p56': 'APCLvl2',
    'p57': 'HeliLvl2',
    'p58': 'TankLvl3',
    'p59': 'APCLvl3',
    'p60': 'HeliLvl3',
    'p61': 'ARRifle',
    'p62': 'AKRifle',
    'p63': 'Pistol',
    'p64': 'HuntingRifle',
    'p65': 'RPG',
    'p66': 'Shotgun',
    'p67': 'SniperRifle',
    'p68': 'SMG',
    'p69': 'Homing',
    'p71': 'Grenade',
    'p74': 'HeliMinigun',
    'p75': 'TankMinigun',
    'p76': 'Knife',
    'p78': 'Revolver',
    'p79': 'Minigun',
    'p80': 'GrenadeLauncher',
    'p81': 'SmokeGrenade',
    'p82': 'Jet1Rockets',
    'p83': 'Jet1Homing',
    'p84': 'Jet1MachineGun',
    'p85': 'Jet2Rockets',
    'p86': 'Jet2Homing',
    'p87': 'Jet2MachineGun',
    'p88': 'Fists',
    'p89': 'VSS',
    'p90': 'FiftyCalSniper',
    'p91': 'MGTurret',
    'p92': 'Crossbow',
    'p93': 'SCAR',
    'p94': 'TacticalShotgun',
    'p95': 'VEK',
    'p96': 'Desert',
    'p97': 'Auto',
    'p98': 'LMG',
    'p99': 'UNRELEASED_WEAPON_99',
    'p100': 'UnreleasedMace',
    'p101': 'RubberChicken',
    'p102': 'UnreleasedButterfly',
    'p103': 'Chainsaw',
    'p104': 'AKSMG',
    'p105': 'AutoSniper',
    'p106': 'UnreleasedAR',
    'p107': 'UnreleasedSawedOff',
    'p108': 'HealingPistol',
    'p109': 'UnreleasedMP7',
    'p110': 'ImplosionGrenade',
    'p111': 'LaserTripMine',
    'p112': 'ConcussionGrenade',
    'p126': 'G3A3'
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
    response.raise_for_status()
    return response.json()

# Function to get squad members
def get_squad_members(squad_name):
    response = requests.get(squad_members_url.format(squad_name))
    response.raise_for_status()
    return response.json()

# Function to get player info
def get_player_info(uid):
    response = requests.get(player_info_url.format(uid))
    response.raise_for_status()
    return response.json()

# Function to map damage dealt to human-readable names
def map_damage_dealt(damage_dealt):
    return {damage_names.get(k, k): v for k, v in damage_dealt.items()}

# Ensure the CSV file exists and has headers
if not os.path.exists(csv_file_path):
    headers = ['Date', 'Squad', 'Name', 'UserID', 'Level', 'XP', 'JoinTime', 'PingTime', 'Banned', 'Coins', 
               'KillsELO', 'GamesELO', 'Number_of_Jumps', 'Zombie_Deaths', 'Zombie_Kills', 'Zombie_Wins', 'Time', 
               'Time_Alive_Count', 'Time_Alive_Longest', 'Time_Alive', 'Zombie_Time_Alive_Count', 'Zombie_Time_Alive'] \
              + list(damage_names.values()) + [f"Losses_{key}" for key in ['m00', 'm10', 'm09', 'm08', 'm07']]
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

# Get the list of squads
squads = get_squad_list()

# Calculate total number of players for the progress bar
total_players = sum(len(get_squad_members(squad)) for squad in squads)

# Create a progress bar for processing players
with tqdm(total=total_players, desc="Processing Players", unit="player") as progress_bar:
    for squad in squads:
        members = get_squad_members(squad)

        for member in members:
            try:
                player_info = get_player_info(member['uid'])

                # Skip if player_info is None
                if not player_info:
                    continue

                # Ensure player_info['losses'] is a dictionary
                losses = player_info.get('losses', {}) if isinstance(player_info.get('losses', {}), dict) else {}

                damage_dealt = map_damage_dealt(player_info.get('damage_dealt', {}))

                # Create a row with all relevant player info
                row = [
                    today,
                    squad,
                    player_info.get('nick'),
                    member['uid'],  # Add UserID to the row
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
                ] + [damage_dealt.get(name, 0) for name in damage_names.values()] \
                  + [losses.get(key, 0) for key in ['m00', 'm10', 'm09', 'm08', 'm07']]

                # Append data to the CSV file
                with open(csv_file_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(row)

            except Exception as e:
                print(f"Error processing user {member['uid']}: {e}")

            # Update the progress bar
            progress_bar.update(1)
