import requests
import csv
import os
from datetime import datetime
from tqdm import tqdm

# Directory and file paths
data_dir = './data/'
csv_file_path = './data/wbuserdata_ts.csv'
temp_csv_file_path = './data/wbuserdata_ts_temp.csv'
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
    'p81': 'Jet1Rockets',
    'p82': 'Jet1Homing',
    'p83': 'Jet1MachineGun',
    'p84': 'Jet2Homing',
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
    'p99': 'b/k',
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

# Function to flatten nested categories
def flatten_nested_categories(data, prefix):
    flattened = {}
    total = 0
    for key, value in data.items():
        flattened[f"{prefix}_{key}"] = value
        total += value
    flattened[f"{prefix}_total"] = total
    return flattened

# Ensure the CSV file exists and has headers
if not os.path.exists(csv_file_path):
    headers = ['Date', 'Squad', 'Name', 'UserID', 'Level', 'XP', 'JoinTime', 'PingTime', 'Banned', 'Coins',
               'KillsELO', 'GamesELO', 'Number_of_Jumps', 'Zombie_Deaths', 'Zombie_Kills', 'Zombie_Wins', 'Time',
               'Time_Alive_Count', 'Time_Alive_Longest', 'Time_Alive', 'Zombie_Time_Alive_Count', 'Zombie_Time_Alive',
               'Scuds_Launched', 'Self_Destructs_v30', 'Self_Destructs_v40', 'Self_Destructs_v41', 'Self_Destructs_v20', 'Self_Destructs_total',
               'Distance_Driven_v10', 'Distance_Driven_v30', 'Distance_Driven_v00', 'Distance_Driven_v40', 'Distance_Driven_v41',
               'Distance_Driven_v20', 'Distance_Driven_v21', 'Distance_Driven_v01', 'Distance_Driven_v11', 'Distance_Driven_v02',
               'Distance_Driven_v22', 'Distance_Driven_v12', 'Distance_Driven_v02', 'Distance_Driven_v22', 'Distance_Driven_v12',
               'Distance_Driven_v13', 'Distance_Driven_v60', 'Distance_Driven_total', 'Distance_Driven_Count_v10',
               'Distance_Driven_Count_v30', 'Distance_Driven_Count_v00', 'Distance_Driven_Count_v40', 'Distance_Driven_Count_v41',
               'Distance_Driven_Count_v20', 'Distance_Driven_Count_v21', 'Distance_Driven_Count_v01', 'Distance_Driven_Count_v11',
               'Distance_Driven_Count_v02', 'Distance_Driven_Count_v22', 'Distance_Driven_Count_v12', 'Distance_Driven_Count_v02',
               'Distance_Driven_Count_v22', 'Distance_Driven_Count_v12', 'Distance_Driven_Count_v13', 'Distance_Driven_Count_v60',
               'Distance_Driven_Count_total', 'Kills_Per_Vehicle_v30', 'Kills_Per_Vehicle_v00', 'Kills_Per_Vehicle_v10',
               'Kills_Per_Vehicle_v40', 'Kills_Per_Vehicle_v01', 'Kills_Per_Vehicle_v21', 'Kills_Per_Vehicle_v02',
               'Kills_Per_Vehicle_v22', 'Kills_Per_Vehicle_v12', 'Kills_Per_Vehicle_v11', 'Kills_Per_Vehicle_v41',
               'Kills_Per_Vehicle_v50', 'Kills_Per_Vehicle_v60', 'Kills_Per_Vehicle_total', 'Shots_Fired_Unzoomed_AirStrike',
               'Shots_Fired_Unzoomed_BGM', 'Shots_Fired_Unzoomed_SCAR', 'Shots_Fired_Unzoomed_HuntingRifle', 'Shots_Fired_Unzoomed_FiftyCalSniper',
               'Shots_Fired_Unzoomed_TankMinigun', 'Shots_Fired_Unzoomed_ARRifle', 'Shots_Fired_Unzoomed_Crossbow', 'Shots_Fired_Unzoomed_APCLvl1',
               'Shots_Fired_Unzoomed_RPG', 'Shots_Fired_Unzoomed_APCLvl2', 'Shots_Fired_Unzoomed_HeliLvl2', 'Shots_Fired_Unzoomed_SniperRifle',
               'Shots_Fired_Unzoomed_HeliLvl1', 'Shots_Fired_Unzoomed_AKRifle', 'Shots_Fired_Unzoomed_HeliMinigun', 'Shots_Fired_Unzoomed_HeliLvl3',
               'Shots_Fired_Unzoomed_APCLvl3', 'Shots_Fired_Unzoomed_Jet1Rockets', 'Shots_Fired_Unzoomed_Jet1Homing', 'Shots_Fired_Unzoomed_Jet1MachineGun',
               'Shots_Fired_Unzoomed_Jet2Homing', 'Shots_Fired_Unzoomed_Jet2Rockets', 'Shots_Fired_Unzoomed_Jet2MachineGun', 'Shots_Fired_Unzoomed_Pistol',
               'Shots_Fired_Unzoomed_Grenade', 'Shots_Fired_Unzoomed_Jet1Homing', 'Shots_Fired_Unzoomed_Fists', 'Shots_Fired_Unzoomed_VSS',
               'Shots_Fired_Unzoomed_MGTurret', 'Shots_Fired_Unzoomed_Revolver', 'Shots_Fired_Unzoomed_Minigun', 'Shots_Fired_Unzoomed_total',
               'Shots_Fired_Zoomed_ARRifle', 'Shots_Fired_Zoomed_HuntingRifle', 'Shots_Fired_Zoomed_FiftyCalSniper', 'Shots_Fired_Zoomed_TankMinigun',
               'Shots_Fired_Zoomed_APCLvl1', 'Shots_Fired_Zoomed_TankMinigun', 'Shots_Fired_Zoomed_HeliMinigun', 'Shots_Fired_Zoomed_SniperRifle',
               'Shots_Fired_Zoomed_HeliLvl1', 'Shots_Fired_Zoomed_AKRifle', 'Shots_Fired_Zoomed_HeliLvl3', 'Shots_Fired_Zoomed_APCLvl3',
               'Shots_Fired_Zoomed_Jet1Rockets', 'Shots_Fired_Zoomed_Jet1Homing', 'Shots_Fired_Zoomed_Jet1MachineGun', 'Shots_Fired_Zoomed_Jet2Homing',
               'Shots_Fired_Zoomed_Jet2Rockets', 'Shots_Fired_Zoomed_Jet2MachineGun', 'Shots_Fired_Zoomed_Pistol', 'Shots_Fired_Zoomed_Crossbow',
               'Shots_Fired_Zoomed_MGTurret', 'Shots_Fired_Zoomed_Revolver', 'Shots_Fired_Zoomed_Minigun', 'Shots_Fired_Zoomed_total',
               'Shots_Hit_Unzoomed_APCLvl1', 'Shots_Hit_Unzoomed_BGM', 'Shots_Hit_Unzoomed_SCAR', 'Shots_Hit_Unzoomed_FiftyCalSniper',
               'Shots_Hit_Unzoomed_TankMinigun', 'Shots_Hit_Unzoomed_ARRifle', 'Shots_Hit_Unzoomed_Crossbow', 'Shots_Hit_Unzoomed_APCLvl2',
               'Shots_Hit_Unzoomed_RPG', 'Shots_Hit_Unzoomed_APCLvl3', 'Shots_Hit_Unzoomed_HeliLvl2', 'Shots_Hit_Unzoomed_SniperRifle',
               'Shots_Hit_Unzoomed_HeliLvl1', 'Shots_Hit_Unzoomed_AKRifle', 'Shots_Hit_Unzoomed_HeliMinigun', 'Shots_Hit_Unzoomed_HeliLvl3',
               'Shots_Hit_Unzoomed_APCLvl3', 'Shots_Hit_Unzoomed_Jet1Rockets', 'Shots_Hit_Unzoomed_Jet1Homing', 'Shots_Hit_Unzoomed_Jet1MachineGun',
               'Shots_Hit_Unzoomed_Jet2Homing', 'Shots_Hit_Unzoomed_Jet2Rockets', 'Shots_Hit_Unzoomed_Jet2MachineGun', 'Shots_Hit_Unzoomed_Pistol',
               'Shots_Hit_Unzoomed_Grenade', 'Shots_Hit_Unzoomed_Jet1Homing', 'Shots_Hit_Unzoomed_Fists', 'Shots_Hit_Unzoomed_VSS',
               'Shots_Hit_Unzoomed_MGTurret', 'Shots_Hit_Unzoomed_Revolver', 'Shots_Hit_Unzoomed_Minigun', 'Shots_Hit_Unzoomed_total',
               'Shots_Hit_Zoomed_ARRifle', 'Shots_Hit_Zoomed_HuntingRifle', 'Shots_Hit_Zoomed_FiftyCalSniper', 'Shots_Hit_Zoomed_TankMinigun',
               'Shots_Hit_Zoomed_APCLvl1', 'Shots_Hit_Zoomed_TankMinigun', 'Shots_Hit_Zoomed_HeliMinigun', 'Shots_Hit_Zoomed_SniperRifle',
               'Shots_Hit_Zoomed_HeliLvl1', 'Shots_Hit_Zoomed_AKRifle', 'Shots_Hit_Zoomed_HeliLvl3', 'Shots_Hit_Zoomed_APCLvl3',
               'Shots_Hit_Zoomed_Jet1Rockets', 'Shots_Hit_Zoomed_Jet1Homing', 'Shots_Hit_Zoomed_Jet1MachineGun', 'Shots_Hit_Zoomed_Jet2Homing',
               'Shots_Hit_Zoomed_Jet2Rockets', 'Shots_Hit_Zoomed_Jet2MachineGun', 'Shots_Hit_Zoomed_Pistol', 'Shots_Hit_Zoomed_Crossbow',
               'Shots_Hit_Zoomed_MGTurret', 'Shots_Hit_Zoomed_Revolver', 'Shots_Hit_Zoomed_Minigun', 'Shots_Hit_Zoomed_total',
               'Damage_Dealt_BGM', 'Damage_Dealt_APCLvl1', 'Damage_Dealt_ARRifle', 'Damage_Dealt_HuntingRifle', 'Damage_Dealt_SCAR',
               'Damage_Dealt_TankMinigun', 'Damage_Dealt_FiftyCalSniper', 'Damage_Dealt_TankLvl1', 'Damage_Dealt_Jet1Rockets',
               'Damage_Dealt_Jet1Homing', 'Damage_Dealt_SmokeGrenade', 'Damage_Dealt_AirStrike', 'Damage_Dealt_AKRifle', 'Damage_Dealt_Jet1MachineGun',
               'Damage_Dealt_Jet2Homing', 'Damage_Dealt_Jet2MachineGun', 'Damage_Dealt_Pistol', 'Damage_Dealt_Crossbow', 'Damage_Dealt_APCLvl2',
               'Damage_Dealt_RPG', 'Damage_Dealt_APCLvl3', 'Damage_Dealt_HeliLvl2', 'Damage_Dealt_SniperRifle', 'Damage_Dealt_HeliLvl1',
               'Damage_Dealt_HeliLvl3', 'Damage_Dealt_AKRifle', 'Damage_Dealt_Jet1Rockets', 'Damage_Dealt_Jet1Homing', 'Damage_Dealt_Jet1MachineGun',
               'Damage_Dealt_Jet2Homing', 'Damage_Dealt_Jet2MachineGun', 'Damage_Dealt_Grenade', 'Damage_Dealt_HeliMinigun', 'Damage_Dealt_HeliLvl3',
               'Damage_Dealt_APCLvl3', 'Damage_Dealt_Jet1Rockets', 'Damage_Dealt_Knife', 'Damage_Dealt_Shotgun', 'Damage_Dealt_SMG',
               'Damage_Dealt_Fists', 'Damage_Dealt_VSS', 'Damage_Dealt_MGTurret', 'Damage_Dealt_Revolver', 'Damage_Dealt_Minigun',
               'Damage_Dealt_GrenadeLauncher', 'Damage_Dealt_HeliMinigun', 'Damage_Dealt_HeliLvl3', 'Damage_Dealt_APCLvl3',
               'Damage_Dealt_Jet1Rockets', 'Damage_Dealt_Jet1Homing', 'Damage_Dealt_Jet1MachineGun', 'Damage_Dealt_Jet2Homing',
               'Damage_Dealt_Jet2MachineGun', 'Damage_Dealt_Pistol', 'Damage_Dealt_Grenade', 'Damage_Dealt_HeliLvl2', 'Damage_Dealt_HeliLvl3',
               'Damage_Dealt_AKRifle', 'Damage_Dealt_Pistol', 'Damage_Dealt_Jet2Homing', 'Damage_Dealt_Jet2MachineGun', 'Damage_Dealt_SniperRifle',
               'Damage_Dealt_HeliLvl1', 'Damage_Dealt_GrenadeLauncher', 'Damage_Dealt_HeliLvl3', 'Damage_Dealt_APCLvl3',
               'Damage_Dealt_Jet1Rockets', 'Damage_Dealt_Knife', 'Damage_Dealt_Shotgun', 'Damage_Dealt_SMG', 'Damage_Dealt_Fists',
               'Damage_Dealt_VSS', 'Damage_Dealt_MGTurret', 'Damage_Dealt_Revolver', 'Damage_Dealt_Minigun', 'Damage_Dealt_GrenadeLauncher',
               'Damage_Dealt_TacticalShotgun', 'Damage_Dealt_VEK', 'Damage_Dealt_Desert', 'Damage_Dealt_Auto', 'Damage_Dealt_LMG',
               'Damage_Dealt_total', 'Damage_Received_HeliLvl2', 'Damage_Received_ARRifle', 'Damage_Received_SCAR', 'Damage_Received_SniperRifle',
               'Damage_Received_Jet1Rockets', 'Damage_Received_Shotgun', 'Damage_Received_APCLvl2', 'Damage_Received_HeliLvl3',
               'Damage_Received_AKRifle', 'Damage_Received_Crossbow', 'Damage_Received_APCLvl3', 'Damage_Received_RPG', 'Damage_Received_TankMinigun',
               'Damage_Received_HeliLvl1', 'Damage_Received_HeliLvl3', 'Damage_Received_GrenadeLauncher', 'Damage_Received_Jet2MachineGun',
               'Damage_Received_Jet2Homing', 'Damage_Received_Jet2Rockets', 'Damage_Received_HuntingRifle', 'Damage_Received_MGTurret',
               'Damage_Received_TacticalShotgun', 'Damage_Received_VEK', 'Damage_Received_Desert', 'Damage_Received_Auto', 'Damage_Received_LMG',
               'Damage_Received_total', 'Kills_Per_Weapon_SCAR', 'Kills_Per_Weapon_HuntingRifle', 'Kills_Per_Weapon_TankMinigun',
               'Kills_Per_Weapon_ARRifle', 'Kills_Per_Weapon_FiftyCalSniper', 'Kills_Per_Weapon_BGM', 'Kills_Per_Weapon_SmokeGrenade',
               'Kills_Per_Weapon_AKRifle', 'Kills_Per_Weapon_Jet1Homing', 'Kills_Per_Weapon_Jet1MachineGun', 'Kills_Per_Weapon_Pistol',
               'Kills_Per_Weapon_Jet2Homing', 'Kills_Per_Weapon_Jet2MachineGun', 'Kills_Per_Weapon_SniperRifle', 'Kills_Per_Weapon_Jet2Rockets',
               'Kills_Per_Weapon_Jet1Rockets', 'Kills_Per_Weapon_Grenade', 'Kills_Per_Weapon_HeliLvl2', 'Kills_Per_Weapon_Shotgun',
               'Kills_Per_Weapon_APCLvl2', 'Kills_Per_Weapon_RPG', 'Kills_Per_Weapon_APCLvl3', 'Kills_Per_Weapon_HeliLvl1',
               'Kills_Per_Weapon_HeliLvl3', 'Kills_Per_Weapon_GrenadeLauncher', 'Kills_Per_Weapon_HeliLvl3', 'Kills_Per_Weapon_APCLvl3',
               'Kills_Per_Weapon_Jet1Rockets', 'Kills_Per_Weapon_Knife', 'Kills_Per_Weapon_Shotgun', 'Kills_Per_Weapon_SMG',
               'Kills_Per_Weapon_Fists', 'Kills_Per_Weapon_VSS', 'Kills_Per_Weapon_MGTurret', 'Kills_Per_Weapon_Revolver',
               'Kills_Per_Weapon_Minigun', 'Kills_Per_Weapon_Jet1Homing', 'Kills_Per_Weapon_Jet2Homing', 'Kills_Per_Weapon_Jet2MachineGun',
               'Kills_Per_Weapon_total', 'Deaths_SniperRifle', 'Deaths_Shotgun', 'Deaths_SMG', 'Deaths_APCLvl2', 'Deaths_HeliLvl3',
               'Deaths_AKRifle', 'Deaths_Crossbow', 'Deaths_Jet1MachineGun', 'Deaths_Pistol', 'Deaths_Grenade',
               'Deaths_HeliMinigun', 'Deaths_Jet2MachineGun', 'Deaths_RPG', 'Deaths_APCLvl3', 'Deaths_HeliLvl1', 'Deaths_Pistol',
               'Deaths_Jet2MachineGun', 'Deaths_GrenadeLauncher', 'Deaths_HeliLvl3', 'Deaths_APCLvl3', 'Deaths_Jet1Rockets',
               'Deaths_Fists', 'Deaths_TankMinigun', 'Deaths_VSS', 'Deaths_Revolver', 'Deaths_Minigun', 'Deaths_SMG',
               'Deaths_Jet2Homing', 'Deaths_Jet1Rockets', 'Deaths_Jet2Rockets', 'Deaths_HuntingRifle', 'Deaths_MGTurret',
               'Deaths_TacticalShotgun', 'Deaths_VEK', 'Deaths_Desert', 'Deaths_Auto', 'Deaths_LMG', 'Deaths_total',
               'Headshots_HuntingRifle', 'Headshots_SCAR', 'Headshots_Jet1MachineGun', 'Headshots_FiftyCalSniper', 'Headshots_ARRifle',
               'Headshots_Jet1Homing', 'Headshots_AKRifle', 'Headshots_Crossbow', 'Headshots_HeliLvl2', 'Headshots_RPG',
               'Headshots_Shotgun', 'Headshots_APCLvl2', 'Headshots_HeliLvl2', 'Headshots_SniperRifle', 'Headshots_HeliLvl1',
               'Headshots_Pistol', 'Headshots_Knife', 'Headshots_Jet2MachineGun', 'Headshots_GrenadeLauncher', 'Headshots_HeliLvl3',
               'Headshots_APCLvl3', 'Headshots_Jet1Rockets', 'Headshots_Fists', 'Headshots_TankMinigun', 'Headshots_VSS',
               'Headshots_Revolver', 'Headshots_Minigun', 'Headshots_SMG', 'Headshots_Jet2Homing', 'Headshots_Jet2Rockets',
               'Headshots_HuntingRifle', 'Headshots_MGTurret', 'Headshots_TacticalShotgun', 'Headshots_VEK', 'Headshots_Desert',
               'Headshots_Auto', 'Headshots_LMG', 'Headshots_total']
    os.makedirs(data_dir, exist_ok=True)
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

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

# Main function to process and append data
def process_and_append_data():
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
                row = [
                    today,
                    player_info.get('squad'),
                    player_info.get('nick'),
                    uid,
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
                    player_info.get('zombie_time_alive'),
                    player_info.get('scuds_launched'),
                ] + list(wins.values()) + list(losses.values()) + list(self_destructs.values()) + list(distance_driven.values()) \
                  + list(distance_driven_count.values()) + list(kills_per_vehicle.values()) + list(shots_fired_unzoomed.values()) \
                  + list(shots_fired_zoomed.values()) + list(shots_hit_unzoomed.values()) + list(shots_hit_zoomed.values()) \
                  + list(damage_dealt.values()) + list(damage_received.values()) + list(kills_per_weapon.values()) \
                  + list(deaths.values()) + list(headshots.values())

                # Append data to the temporary CSV file
                with open(temp_csv_file_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(row)

            except Exception as e:
                print(f"Error processing user {uid}: {e}")

            # Update the progress bar
            progress_bar.update(1)

    # Move the temporary CSV file to the final CSV file
    os.replace(temp_csv_file_path, csv_file_path)

# Run the script
if __name__ == "__main__":
    process_and_append_data()
