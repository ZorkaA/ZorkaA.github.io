import requests
import os
from datetime import datetime
from tqdm import tqdm
from supabase import create_client, Client

# Supabase configuration
supabase_url = 'https://vviprqpyqkwjdtqqlmde.supabase.co'
supabase_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ2aXBycXB5cWt3amR0cXFsbWRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAxMDUxNzMsImV4cCI6MjA0NTY4MTE3M30.ftmjdgdJPjOox5SpxDNoQ3kJX0vfbhRoEHharLcI4eM'
supabase: Client = create_client(supabase_url, supabase_key)

# Directory and file paths
data_dir = './data/'
uids_file_path = './data/uniqueuids.txt'

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
    'p99': 'KBAR',
    'p100': 'Mace',
    'p101': 'RubberChicken',
    'p102': 'Butterfly',
    'p103': 'Chainsaw',
    'p104': 'AKSMG',
    'p105': 'AutoSniper',
    'p106': 'G36',
    'p107': 'SawedOff',
    'p108': 'HealingPistol',
    'p109': 'MP7',
    'p110': 'ImplosionGrenade',
    'p111': 'LaserTripMine',
    'p112': 'ConcussionGrenade',
    'p126': 'G3A3',
}

# API URLs
squad_list_url = "https://wbapi.wbpjs.com/squad/getSquadList"
squad_members_url = "https://wbapi.wbpjs.com/squad/getSquadMembers?squadName={}"
player_info_url = "https://wbapi.wbpjs.com/players/getPlayer?uid={}"

# Get the current date
today = datetime.today().strftime('%m%d%Y')

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

# Function to flatten nested categories
def flatten_nested_categories(data, prefix):
    flattened = {}
    total = 0
    for key, value in data.items():
        flattened[f"{prefix}_{key}"] = value
        total += value
    flattened[f"{prefix}_total"] = total
    return flattened

# Ensure the directory exists
os.makedirs(data_dir, exist_ok=True)

# Collect unique user IDs
def collect_unique_uids():
    squads = get_squad_list()
    unique_uids = set()

    # Read existing UIDs from file
    if os.path.exists(uids_file_path):
        with open(uids_file_path, 'r') as file:
            unique_uids.update(line.strip() for line in file)

    # Collect new UIDs from squad members
    for squad in squads:
        members = get_squad_members(squad)
        for member in members:
            unique_uids.add(member['uid'])

    # Write updated UIDs to file
    with open(uids_file_path, 'w') as file:
        for uid in unique_uids:
            file.write(f"{uid}\n")

    return unique_uids

# Function to insert data into Supabase
def insert_data_into_supabase(data):
    response = supabase.table('wbtsdb').insert(data).execute()
    if response.get('error'):
        print(f"Error inserting data: {response['error']}")
    else:
        print(f"Data inserted successfully: {response['data']}")

# Main function to process and insert data
def process_and_insert_data():
    unique_uids = collect_unique_uids()

    # Calculate total number of players for the progress bar
    total_players = len(unique_uids)

    # Create a progress bar for processing players
    with tqdm(total=total_players, desc="Processing Players", unit="player") as progress_bar:
        for uid in unique_uids:
            try:
                player_info = get_player_info(uid)

                # Skip if player_info is None
                if not player_info:
                    continue

                # Flatten nested categories
                wins = flatten_nested_categories(player_info.get('wins', {}), 'wins')
                losses = flatten_nested_categories(player_info.get('losses', {}), 'losses')
                self_destructs = flatten_nested_categories(player_info.get('self_destructs', {}), 'self_destructs')
                distance_driven = flatten_nested_categories(player_info.get('distance_driven', {}), 'distance_driven')
                distance_driven_count = flatten_nested_categories(player_info.get('distance_driven_count', {}), 'distance_driven_count')
                kills_per_vehicle = flatten_nested_categories(player_info.get('kills_per_vehicle', {}), 'kills_per_vehicle')
                shots_fired_unzoomed = flatten_nested_categories(player_info.get('shots_fired_unzoomed', {}), 'shots_fired_unzoomed')
                shots_fired_zoomed = flatten_nested_categories(player_info.get('shots_fired_zoomed', {}), 'shots_fired_zoomed')
                shots_hit_unzoomed = flatten_nested_categories(player_info.get('shots_hit_unzoomed', {}), 'shots_hit_unzoomed')
                shots_hit_zoomed = flatten_nested_categories(player_info.get('shots_hit_zoomed', {}), 'shots_hit_zoomed')
                damage_dealt = flatten_nested_categories(map_damage_dealt(player_info.get('damage_dealt', {})), 'damage_dealt')
                damage_received = flatten_nested_categories(player_info.get('damage_received', {}), 'damage_received')
                kills_per_weapon = flatten_nested_categories(player_info.get('kills_per_weapon', {}), 'kills_per_weapon')
                deaths = flatten_nested_categories(player_info.get('deaths', {}), 'deaths')
                headshots = flatten_nested_categories(player_info.get('headshots', {}), 'headshots')

                # Create a row with all relevant player info
                row = {
                    'Date': today,
                    'Squad': player_info.get('squad'),
                    'Name': player_info.get('nick'),
                    'UserID': uid,
                    'Level': player_info.get('level'),
                    'XP': player_info.get('xp'),
                    'JoinTime': player_info.get('joinTime'),
                    'PingTime': player_info.get('ping_time'),
                    'Banned': player_info.get('banned'),
                    'Coins': player_info.get('coins'),
                    'KillsELO': player_info.get('killsELO'),
                    'GamesELO': player_info.get('gamesELO'),
                    'Number_of_Jumps': player_info.get('number_of_jumps'),
                    'Zombie_Deaths': player_info.get('zombie_deaths'),
                    'Zombie_Kills': player_info.get('zombie_kills'),
                    'Zombie_Wins': player_info.get('zombie_wins'),
                    'Time': player_info.get('time'),
                    'Time_Alive_Count': player_info.get('time_alive_count'),
                    'Time_Alive_Longest': player_info.get('time_alive_longest'),
                    'Time_Alive': player_info.get('time_alive'),
                    'Zombie_Time_Alive_Count': player_info.get('zombie_time_alive_count'),
                    'Zombie_Time_Alive': player_info.get('zombie_time_alive'),
                    'Scuds_Launched': player_info.get('scuds_launched')
                }
                row.update(wins)
                row.update(losses)
                row.update(self_destructs)
                row.update(distance_driven)
                row.update(distance_driven_count)
                row.update(kills_per_vehicle)
                row.update(shots_fired_unzoomed)
                row.update(shots_fired_zoomed)
                row.update(shots_hit_unzoomed)
                row.update(shots_hit_zoomed)
                row.update(damage_dealt)
                row.update(damage_received)
                row.update(kills_per_weapon)
                row.update(deaths)
                row.update(headshots)

                # Insert data into Supabase
                insert_data_into_supabase(row)

            except Exception as e:
                print(f"Error processing user {uid}: {e}")

            # Update the progress bar
            progress_bar.update(1)

# Run the script
if __name__ == "__main__":
    process_and_insert_data()
