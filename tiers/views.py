import requests
import urllib.request

from django.shortcuts import render
from django.utils.safestring import SafeString

from tiers.constants import lineup_dict, position_dict, tier_url

# Create your views here.


def all_players(request, league_id, year='2020'):
    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?&view=kona_player_info')
    players = response.json()['players']

    player_dict = {}
    for player in players:
        temp = {'id': player['id'],
                'name': player['player']['fullName'],
                'position': position_dict[player['player']['defaultPositionId']],
                'status': player['status']}
        player_dict[temp['id']] = temp

    context = {'players': player_dict}

    print(player_dict)

    return render(request, 'tiers/all_players.html', context)


def view_team(request, team_id, league_id, year='2020'):
    # Get team info
    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}')
    team_info = [x for x in response.json()['teams'] if x['id'] == team_id][0]
    team_name = f'{team_info["location"]} {team_info["nickname"]}'

    # Get roster info
    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?forTeamId={team_id}&view=mRoster')
    roster = response.json()['teams'][0]['roster']['entries']

    roster_dict = {}

    for player in roster:
        temp = {'id': player['playerId'],
                'lineup_slot': lineup_dict[player['lineupSlotId']],
                'name': player['playerPoolEntry']['player']['fullName'],
                'position': position_dict[player['playerPoolEntry']['player']['defaultPositionId']],
                'status': player['playerPoolEntry']['player']['injured']}
        roster_dict[temp['id']] = temp

    context = {'team_name': team_name,
               'roster': roster_dict}

    return render(request, 'tiers/view_team.html', context)


def view_tiers(request, scoring, position):
    if scoring == 'standard':
        with urllib.request.urlopen(tier_url.replace('{p}', position).replace('{s}', '')) as url:
            tiers = url.read().decode('utf-8').rstrip().split('\n')
    else:
        with urllib.request.urlopen(tier_url.replace('{p}', position).replace('{s}', f'-{scoring}')) as url:
            tiers = url.read().decode('utf-8').rstrip().split('\n')

    tier_dict = {}
    for tier in tiers:
        # Split tier into tier name and players
        tier = tier.split(': ')
        tier_dict[tier[0]] = tier[1]

    context = {'tiers': tier_dict}

    return render(request, 'tiers/tiers.html', context)
