import requests
import csv
import os
from datetime import datetime
from tqdm import tqdm

# Directory and file paths
data_dir = '/Users/jack/Downloads/'
csv_file_path = os.path.join(data_dir, 'wbuserdata_ts.csv')
uids_file_path = os.path.join(data_dir, 'uniqueuids.txt')

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
    'p99': 'unreleased_B_melee',
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
               'Scuds_Launched', 'Self_Destructs_v30', 'Self_Destructs_v40', 'Self_Destructs_v41', 'Self_Destructs_v20',
               'Self_Destructs_total', 'Distance_Driven_v10', 'Distance_Driven_v30', 'Distance_Driven_v00',
               'Distance_Driven_v40', 'Distance_Driven_v41', 'Distance_Driven_v20', 'Distance_Driven_v21',
               'Distance_Driven_v01', 'Distance_Driven_v11', 'Distance_Driven_v02', 'Distance_Driven_v22',
               'Distance_Driven_v12', 'Distance_Driven_v23', 'Distance_Driven_v13', 'Distance_Driven_v60',
               'Distance_Driven_total', 'Distance_Driven_Count_v10', 'Distance_Driven_Count_v30',
               'Distance_Driven_Count_v00', 'Distance_Driven_Count_v40', 'Distance_Driven_Count_v41',
               'Distance_Driven_Count_v20', 'Distance_Driven_Count_v21', 'Distance_Driven_Count_v01',
               'Distance_Driven_Count_v11', 'Distance_Driven_Count_v02', 'Distance_Driven_Count_v22',
               'Distance_Driven_Count_v12', 'Distance_Driven_Count_v23', 'Distance_Driven_Count_v13',
               'Distance_Driven_Count_v60', 'Distance_Driven_Count_total', 'Kills_Per_Vehicle_v30', 'Kills_Per_Vehicle_v00',
               'Kills_Per_Vehicle_v10', 'Kills_Per_Vehicle_v40', 'Kills_Per_Vehicle_v01', 'Kills_Per_Vehicle_v21',
               'Kills_Per_Vehicle_v02', 'Kills_Per_Vehicle_v22', 'Kills_Per_Vehicle_v12', 'Kills_Per_Vehicle_v11',
               'Kills_Per_Vehicle_v41', 'Kills_Per_Vehicle_v20', 'Kills_Per_Vehicle_v13', 'Kills_Per_Vehicle_v50',
               'Kills_Per_Vehicle_v60', 'Kills_Per_Vehicle_total', 'Shots_Fired_Unzoomed_p11', 'Shots_Fired_Unzoomed_p53',
               'Shots_Fired_Unzoomed_p93', 'Shots_Fired_Unzoomed_p64', 'Shots_Fired_Unzoomed_p90',
               'Shots_Fired_Unzoomed_p75', 'Shots_Fired_Unzoomed_p52', 'Shots_Fired_Unzoomed_p61',
               'Shots_Fired_Unzoomed_p71', 'Shots_Fired_Unzoomed_p83', 'Shots_Fired_Unzoomed_p84',
               'Shots_Fired_Unzoomed_p09', 'Shots_Fired_Unzoomed_p62', 'Shots_Fired_Unzoomed_p85',
               'Shots_Fired_Unzoomed_p86', 'Shots_Fired_Unzoomed_p63', 'Shots_Fired_Unzoomed_p92',
               'Shots_Fired_Unzoomed_p65', 'Shots_Fired_Unzoomed_p54', 'Shots_Fired_Unzoomed_p55',
               'Shots_Fired_Unzoomed_p82', 'Shots_Fired_Unzoomed_p56', 'Shots_Fired_Unzoomed_p57',
               'Shots_Fired_Unzoomed_p67', 'Shots_Fired_Unzoomed_p80', 'Shots_Fired_Unzoomed_p60',
               'Shots_Fired_Unzoomed_p59', 'Shots_Fired_Unzoomed_p85', 'Shots_Fired_Unzoomed_p94',
               'Shots_Fired_Unzoomed_p87', 'Shots_Fired_Unzoomed_p66', 'Shots_Fired_Unzoomed_p88',
               'Shots_Fired_Unzoomed_p68', 'Shots_Fired_Unzoomed_p78', 'Shots_Fired_Unzoomed_p79',
               'Shots_Fired_Unzoomed_p89', 'Shots_Fired_Unzoomed_p74', 'Shots_Fired_Unzoomed_p69',
               'Shots_Fired_Unzoomed_p95', 'Shots_Fired_Unzoomed_p111', 'Shots_Fired_Unzoomed_p98',
               'Shots_Fired_Unzoomed_p101', 'Shots_Fired_Unzoomed_p112', 'Shots_Fired_Unzoomed_p97',
               'Shots_Fired_Unzoomed_p105', 'Shots_Fired_Unzoomed_p96', 'Shots_Fired_Unzoomed_p110',
               'Shots_Fired_Unzoomed_p103', 'Shots_Fired_Unzoomed_p104', 'Shots_Fired_Unzoomed_p126',
               'Shots_Fired_Unzoomed_total', 'Shots_Fired_Zoomed_p61', 'Shots_Fired_Zoomed_p64', 'Shots_Fired_Zoomed_p93',
               'Shots_Fired_Zoomed_p53', 'Shots_Fired_Zoomed_p75', 'Shots_Fired_Zoomed_p52', 'Shots_Fired_Zoomed_p74',
               'Shots_Fired_Zoomed_p82', 'Shots_Fired_Zoomed_p62', 'Shots_Fired_Zoomed_p92', 'Shots_Fired_Zoomed_p65',
               'Shots_Fired_Zoomed_p57', 'Shots_Fired_Zoomed_p84', 'Shots_Fired_Zoomed_p66', 'Shots_Fired_Zoomed_p55',
               'Shots_Fired_Zoomed_p56', 'Shots_Fired_Zoomed_p63', 'Shots_Fired_Zoomed_p67', 'Shots_Fired_Zoomed_p58',
               'Shots_Fired_Zoomed_p80', 'Shots_Fired_Zoomed_p60', 'Shots_Fired_Zoomed_p59', 'Shots_Fired_Zoomed_p90',
               'Shots_Fired_Zoomed_p85', 'Shots_Fired_Zoomed_p94', 'Shots_Fired_Zoomed_p87', 'Shots_Fired_Zoomed_p54',
               'Shots_Fired_Zoomed_p68', 'Shots_Fired_Zoomed_p86', 'Shots_Fired_Zoomed_p88', 'Shots_Fired_Zoomed_p69',
               'Shots_Fired_Zoomed_p89', 'Shots_Fired_Zoomed_p91', 'Shots_Fired_Zoomed_p83', 'Shots_Fired_Zoomed_p98',
               'Shots_Fired_Zoomed_p112', 'Shots_Fired_Zoomed_p79', 'Shots_Fired_Zoomed_p97', 'Shots_Fired_Zoomed_p105',
               'Shots_Fired_Zoomed_p96', 'Shots_Fired_Zoomed_p101', 'Shots_Fired_Zoomed_p71', 'Shots_Fired_Zoomed_p104',
               'Shots_Fired_Zoomed_p126', 'Shots_Fired_Zoomed_total', 'Shots_Hit_Unzoomed_p53', 'Shots_Hit_Unzoomed_p11',
               'Shots_Hit_Unzoomed_p93', 'Shots_Hit_Unzoomed_p90', 'Shots_Hit_Unzoomed_p52', 'Shots_Hit_Unzoomed_p61',
               'Shots_Hit_Unzoomed_p83', 'Shots_Hit_Unzoomed_p62', 'Shots_Hit_Unzoomed_p09', 'Shots_Hit_Unzoomed_p86',
               'Shots_Hit_Unzoomed_p92', 'Shots_Hit_Unzoomed_p54', 'Shots_Hit_Unzoomed_p65', 'Shots_Hit_Unzoomed_p63',
               'Shots_Hit_Unzoomed_p55', 'Shots_Hit_Unzoomed_p56', 'Shots_Hit_Unzoomed_p71', 'Shots_Hit_Unzoomed_p57',
               'Shots_Hit_Unzoomed_p67', 'Shots_Hit_Unzoomed_p58', 'Shots_Hit_Unzoomed_p80', 'Shots_Hit_Unzoomed_p76',
               'Shots_Hit_Unzoomed_p60', 'Shots_Hit_Unzoomed_p85', 'Shots_Hit_Unzoomed_p94', 'Shots_Hit_Unzoomed_p66',
               'Shots_Hit_Unzoomed_p59', 'Shots_Hit_Unzoomed_p75', 'Shots_Hit_Unzoomed_p78', 'Shots_Hit_Unzoomed_p88',
               'Shots_Hit_Unzoomed_p68', 'Shots_Hit_Unzoomed_p89', 'Shots_Hit_Unzoomed_p79', 'Shots_Hit_Unzoomed_p84',
               'Shots_Hit_Unzoomed_p87', 'Shots_Hit_Unzoomed_p82', 'Shots_Hit_Unzoomed_p69', 'Shots_Hit_Unzoomed_p91',
               'Shots_Hit_Unzoomed_p95', 'Shots_Hit_Unzoomed_p64', 'Shots_Hit_Unzoomed_p111', 'Shots_Hit_Unzoomed_p98',
               'Shots_Hit_Unzoomed_p101', 'Shots_Hit_Unzoomed_p112', 'Shots_Hit_Unzoomed_p97', 'Shots_Hit_Unzoomed_p105',
               'Shots_Hit_Unzoomed_p96', 'Shots_Hit_Unzoomed_p110', 'Shots_Hit_Unzoomed_p104', 'Shots_Hit_Unzoomed_p103',
               'Shots_Hit_Unzoomed_p126', 'Shots_Hit_Unzoomed_total', 'Shots_Hit_Zoomed_p93', 'Shots_Hit_Zoomed_p64',
               'Shots_Hit_Zoomed_p61', 'Shots_Hit_Zoomed_p75', 'Shots_Hit_Zoomed_p52', 'Shots_Hit_Zoomed_p82',
               'Shots_Hit_Zoomed_p62', 'Shots_Hit_Zoomed_p92', 'Shots_Hit_Zoomed_p57', 'Shots_Hit_Zoomed_p53',
               'Shots_Hit_Zoomed_p84', 'Shots_Hit_Zoomed_p56', 'Shots_Hit_Zoomed_p63', 'Shots_Hit_Zoomed_p67',
               'Shots_Hit_Zoomed_p58', 'Shots_Hit_Zoomed_p60', 'Shots_Hit_Zoomed_p59', 'Shots_Hit_Zoomed_p90',
               'Shots_Hit_Zoomed_p85', 'Shots_Hit_Zoomed_p87', 'Shots_Hit_Zoomed_p65', 'Shots_Hit_Zoomed_p54',
               'Shots_Hit_Zoomed_p94', 'Shots_Hit_Zoomed_p68', 'Shots_Hit_Zoomed_p55', 'Shots_Hit_Zoomed_p89',
               'Shots_Hit_Zoomed_p91', 'Shots_Hit_Zoomed_p74', 'Shots_Hit_Zoomed_p78', 'Shots_Hit_Zoomed_p66',
               'Shots_Hit_Zoomed_p95', 'Shots_Hit_Zoomed_p86', 'Shots_Hit_Zoomed_p83', 'Shots_Hit_Zoomed_p80',
               'Shots_Hit_Zoomed_p98', 'Shots_Hit_Zoomed_p112', 'Shots_Hit_Zoomed_p79', 'Shots_Hit_Zoomed_p97',
               'Shots_Hit_Zoomed_p105', 'Shots_Hit_Zoomed_p96', 'Shots_Hit_Zoomed_p104', 'Shots_Hit_Zoomed_p71',
               'Shots_Hit_Zoomed_p126', 'Shots_Hit_Zoomed_total', 'Damage_Dealt_p11', 'Damage_Dealt_p53',
               'Damage_Dealt_p61', 'Damage_Dealt_p64', 'Damage_Dealt_p93', 'Damage_Dealt_p75', 'Damage_Dealt_p90',
               'Damage_Dealt_p52', 'Damage_Dealt_p82', 'Damage_Dealt_p83', 'Damage_Dealt_p09', 'Damage_Dealt_p62',
               'Damage_Dealt_p86', 'Damage_Dealt_p92', 'Damage_Dealt_p54', 'Damage_Dealt_p65', 'Damage_Dealt_p57',
               'Damage_Dealt_p55', 'Damage_Dealt_p84', 'Damage_Dealt_p56', 'Damage_Dealt_p71', 'Damage_Dealt_p63',
               'Damage_Dealt_p67', 'Damage_Dealt_p58', 'Damage_Dealt_p80', 'Damage_Dealt_p76', 'Damage_Dealt_p60',
               'Damage_Dealt_p59', 'Damage_Dealt_p85', 'Damage_Dealt_p94', 'Damage_Dealt_p87', 'Damage_Dealt_p66',
               'Damage_Dealt_p78', 'Damage_Dealt_p88', 'Damage_Dealt_p68', 'Damage_Dealt_p79', 'Damage_Dealt_p89',
               'Damage_Dealt_p91', 'Damage_Dealt_p74', 'Damage_Dealt_p69', 'Damage_Dealt_p95', 'Damage_Dealt_p111',
               'Damage_Dealt_p98', 'Damage_Dealt_p101', 'Damage_Dealt_p112', 'Damage_Dealt_p97', 'Damage_Dealt_p105',
               'Damage_Dealt_p96', 'Damage_Dealt_p110', 'Damage_Dealt_p103', 'Damage_Dealt_p104', 'Damage_Dealt_p126',
               'Damage_Dealt_total', 'Damage_Received_p57', 'Damage_Received_p61', 'Damage_Received_p93',
               'Damage_Received_p67', 'Damage_Received_p82', 'Damage_Received_p68', 'Damage_Received_p55',
               'Damage_Received_p52', 'Damage_Received_p69', 'Damage_Received_p75', 'Damage_Received_p62',
               'Damage_Received_p71', 'Damage_Received_p65', 'Damage_Received_p64', 'Damage_Received_p79',
               'Damage_Received_p86', 'Damage_Received_p58', 'Damage_Received_p09', 'Damage_Received_p11',
               'Damage_Received_p92', 'Damage_Received_p90', 'Damage_Received_p83', 'Damage_Received_p80',
               'Damage_Received_p56', 'Damage_Received_p54', 'Damage_Received_p53', 'Damage_Received_p78',
               'Damage_Received_p66', 'Damage_Received_p91', 'Damage_Received_p59', 'Damage_Received_p94',
               'Damage_Received_p63', 'Damage_Received_p60', 'Damage_Received_p76', 'Damage_Received_p88',
               'Damage_Received_p89', 'Damage_Received_p84', 'Damage_Received_p74', 'Damage_Received_p85',
               'Damage_Received_p87', 'Damage_Received_p95', 'Damage_Received_p111', 'Damage_Received_p98',
               'Damage_Received_p112', 'Damage_Received_p101', 'Damage_Received_p97', 'Damage_Received_p105',
               'Damage_Received_p96', 'Damage_Received_p110', 'Damage_Received_p103', 'Damage_Received_p104',
               'Damage_Received_p126', 'Damage_Received_total', 'Kills_Per_Weapon_p93', 'Kills_Per_Weapon_p64',
               'Kills_Per_Weapon_p75', 'Kills_Per_Weapon_p61', 'Kills_Per_Weapon_p90', 'Kills_Per_Weapon_p11',
               'Kills_Per_Weapon_p09', 'Kills_Per_Weapon_p62', 'Kills_Per_Weapon_p92', 'Kills_Per_Weapon_p52',
               'Kills_Per_Weapon_p53', 'Kills_Per_Weapon_p84', 'Kills_Per_Weapon_p55', 'Kills_Per_Weapon_p63',
               'Kills_Per_Weapon_p57', 'Kills_Per_Weapon_p58', 'Kills_Per_Weapon_p67', 'Kills_Per_Weapon_p76',
               'Kills_Per_Weapon_p80', 'Kills_Per_Weapon_p71', 'Kills_Per_Weapon_p60', 'Kills_Per_Weapon_p59',
               'Kills_Per_Weapon_p56', 'Kills_Per_Weapon_p86', 'Kills_Per_Weapon_p94', 'Kills_Per_Weapon_p66',
               'Kills_Per_Weapon_p83', 'Kills_Per_Weapon_p65', 'Kills_Per_Weapon_p54', 'Kills_Per_Weapon_p68',
               'Kills_Per_Weapon_p79', 'Kills_Per_Weapon_p89', 'Kills_Per_Weapon_p78', 'Kills_Per_Weapon_p91',
               'Kills_Per_Weapon_p82', 'Kills_Per_Weapon_p85', 'Kills_Per_Weapon_p74', 'Kills_Per_Weapon_p69',
               'Kills_Per_Weapon_p87', 'Kills_Per_Weapon_p88', 'Kills_Per_Weapon_p95', 'Kills_Per_Weapon_p111',
               'Kills_Per_Weapon_p98', 'Kills_Per_Weapon_p101', 'Kills_Per_Weapon_p97', 'Kills_Per_Weapon_p112',
               'Kills_Per_Weapon_p105', 'Kills_Per_Weapon_p96', 'Kills_Per_Weapon_p104', 'Kills_Per_Weapon_p126',
               'Kills_Per_Weapon_p110', 'Kills_Per_Weapon_total', 'Deaths_p67', 'Deaths_p68', 'Deaths_p55',
               'Deaths_p75', 'Deaths_p62', 'Deaths_p93', 'Deaths_p64', 'Deaths_p79', 'Deaths_p69', 'Deaths_p58',
               'Deaths_p11', 'Deaths_p61', 'Deaths_p92', 'Deaths_p90', 'Deaths_p71', 'Deaths_p09', 'Deaths_p57',
               'Deaths_p78', 'Deaths_p52', 'Deaths_p66', 'Deaths_p94', 'Deaths_p53', 'Deaths_p65', 'Deaths_p63',
               'Deaths_p80', 'Deaths_p88', 'Deaths_p89', 'Deaths_p76', 'Deaths_p59', 'Deaths_p60', 'Deaths_p91',
               'Deaths_p56', 'Deaths_p84', 'Deaths_p85', 'Deaths_p54', 'Deaths_p86', 'Deaths_p83', 'Deaths_p95',
               'Deaths_p111', 'Deaths_p98', 'Deaths_p74', 'Deaths_p112', 'Deaths_p101', 'Deaths_p97', 'Deaths_p87',
               'Deaths_p105', 'Deaths_p96', 'Deaths_p103', 'Deaths_p104', 'Deaths_p126', 'Deaths_total',
               'Headshots_p64', 'Headshots_p93', 'Headshots_p53', 'Headshots_p62', 'Headshots_p90', 'Headshots_p84',
               'Headshots_p61', 'Headshots_p63', 'Headshots_p57', 'Headshots_p67', 'Headshots_p59', 'Headshots_p56',
               'Headshots_p94', 'Headshots_p66', 'Headshots_p75', 'Headshots_p78', 'Headshots_p68', 'Headshots_p89',
               'Headshots_p79', 'Headshots_p91', 'Headshots_p87', 'Headshots_p74', 'Headshots_p52', 'Headshots_p55',
               'Headshots_p95', 'Headshots_p58', 'Headshots_p98', 'Headshots_p97', 'Headshots_p105', 'Headshots_p96',
               'Headshots_p104', 'Headshots_p126', 'Headshots_total'
               ]
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
                    player_info.get('scuds_launched')
                ] + list(wins.values()) + list(losses.values()) + list(self_destructs.values()) + list(distance_driven.values()) \
                  + list(distance_driven_count.values()) + list(kills_per_vehicle.values()) + list(shots_fired_unzoomed.values()) \
                  + list(shots_fired_zoomed.values()) + list(shots_hit_unzoomed.values()) + list(shots_hit_zoomed.values()) \
                  + list(damage_dealt.values()) + list(damage_received.values()) + list(kills_per_weapon.values()) \
                  + list(deaths.values()) + list(headshots.values())

                # Append data to the CSV file
                with open(csv_file_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(row)

            except Exception as e:
                print(f"Error processing user {uid}: {e}")

            # Update the progress bar
            progress_bar.update(1)

# Run the script
if __name__ == "__main__":
    process_and_append_data()
