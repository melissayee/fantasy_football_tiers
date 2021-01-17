import requests
import urllib.request
import json
import re

from django.shortcuts import render
from operator import itemgetter

from tiers.constants import lineup_dict, lineup_order, position_dict, tier_url, team_ids

# Create your views here.


def all_players(request, league_id, scoring='standard', year='2020'):

    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?&view=kona_player_info',
                            headers={'x-fantasy-filter': json.dumps({"players": {"filterStatus": {"value": ["FREEAGENT", "WAIVERS"]}}})})
    players = response.json()['players']

    # Get tiers
    tiers = {}

    for position_id, position_name in position_dict.items():
        if position_name == 'D/ST':
            position_name = 'DST'

        tiers[position_name] = get_tiers(scoring, position_name)

    # Update DST to D/ST
    tiers['D/ST'] = tiers.pop('DST')

    # Organize Free Agents by position
    player_dict = {position_dict[position]: [] for position in position_dict}

    for player in players:

        # If player's position doesn't exist in tier (ie. not in lineup_dict constant), ignore the player
        if player['player']['defaultPositionId'] in position_dict:

            temp = {'id': player['id'],
                    'name': player['player']['fullName'],
                    'status': player['status'],
                    'position': position_dict[player['player']['defaultPositionId']],
                    'team': player['player']['proTeamId'],
                    'tier': 'Not Ranked'}

            for tier in tiers[temp['position']]:
                # Change the name of the DST team to match the source (ie. Rams D/ST to Los Angeles Rams)
                if temp['position'] == 'D/ST':
                    name = team_ids[temp['team']]
                else:
                    name = temp['name']

                if name in tier[1]:
                    # Gets the actual tier number from the Tier string for ordering
                    temp['tier'] = int((re.search(r'\d+$', tier[0])).group())

            # If the player is not ranked, don't include them in the results
            if temp['tier'] != 'Not Ranked':
                player_dict[temp['position']].append(temp)

    # Reorder the dictionaries by tier so they can be displayed in ascending order
    ordered_players = {}
    for position, value in player_dict.items():
        ordered_players[position] = sorted(value, key=itemgetter('tier'))

    context = {'players': ordered_players}

    return render(request, 'tiers/all_players.html', context)


def view_team(request, team_id, league_id, scoring='standard', year='2020'):
    # Get team info
    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}')
    team_info = [x for x in response.json()['teams'] if x['id'] == team_id][0]
    team_name = f'{team_info["location"]} {team_info["nickname"]}'

    # Get roster info
    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?forTeamId={team_id}&view=mRoster')
    roster = response.json()['teams'][0]['roster']['entries']

    tiers = {}

    # Get tiers for all positions
    for position_id, position_name in position_dict.items():
        if position_name == 'D/ST':
            position_name = 'DST'

        tiers[position_name] = get_tiers(scoring, position_name)

    # Update DST to D/ST
    tiers['D/ST'] = tiers.pop('DST')

    # Match players in roster with their tier
    roster_dict = {}

    for player in roster:
        temp = {'id': player['playerId'],
                'lineup_slot': lineup_dict[player['lineupSlotId']],
                'name': player['playerPoolEntry']['player']['fullName'],
                'team': player['playerPoolEntry']['player']['proTeamId'],
                'position': position_dict[player['playerPoolEntry']['player']['defaultPositionId']],
                'status': player['playerPoolEntry']['player']['injured'],
                'tier': 'Not Ranked'}

        for tier in tiers[temp['position']]:
            # Change the name of the DST team to match the source (ie. Rams D/ST to Los Angeles Rams)
            if temp['position'] == 'D/ST':
                name = team_ids[temp['team']]
            else:
                name = temp['name']

            if name in tier[1]:
                temp['tier'] = tier[0]

        # Set the lineup order values
        temp['lineup_order'] = lineup_order[temp['lineup_slot']]

        roster_dict[temp['id']] = temp

    # Reorder the dictionary to appear in proper lineup order to match ESPN
    lst = sorted(roster_dict, key=lambda x: (roster_dict[x]['lineup_order']))
    roster_dict = {k: roster_dict[k] for k in lst}

    context = {'team_name': team_name,
               'roster': roster_dict}

    return render(request, 'tiers/view_team.html', context)


def view_tiers(request, scoring, position):
    tiers = get_tiers(scoring, position)
    tier_dict = {}
    for tier in tiers:
        tier_dict[tier[0]] = tier[1]

    context = {'tiers': tier_dict}

    return render(request, 'tiers/tiers.html', context)


# Gets the list of tiers from borischen.co based on the scoring type and the position
def get_tiers(scoring, position):
    if scoring == 'standard':
        with urllib.request.urlopen(tier_url.replace('{p}', position).replace('{s}', '')) as url:
            tiers = url.read().decode('utf-8').rstrip().split('\n')
    else:
        with urllib.request.urlopen(tier_url.replace('{p}', position).replace('{s}', f'-{scoring}')) as url:
            tiers = url.read().decode('utf-8').rstrip().split('\n')

    tier_list = []
    for tier in tiers:
        # Split tier into tier name and players
        tier = tier.split(': ')
        tier_list.append(tier)

    return tier_list
