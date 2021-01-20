import json
import re
import requests
import urllib.request

from django.shortcuts import render, redirect
from operator import itemgetter
from urllib.parse import parse_qs

from tiers.constants import lineup_dict, lineup_order, position_dict, season, tier_url, team_ids
from tiers.forms import TeamForm

# Create your views here.


def home(request):
    # If the user has submitted their ESPN url and scoring
    if request.method == 'POST':
        # Check whether form is valid
        form = TeamForm(request.POST)
        if form.is_valid():
            parsed_url = urllib.parse.urlparse(form.cleaned_data['url'])

            league_id = parse_qs(parsed_url.query)['leagueId'][0]
            team_id = parse_qs(parsed_url.query)['teamId'][0]

            # Redirect the the team page
            return redirect('team', scoring=form.cleaned_data['scoring'], league_id=league_id, team_id=team_id)

        else:
            return redirect('home')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TeamForm()
    context = {'form': form}

    return render(request, 'tiers/home.html', context)


def all_players(request, league_id, scoring='standard', year=season):
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


def view_team(request, team_id, league_id, scoring='standard', year=season):
    # Get team info
    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}')
    team_info = [x for x in response.json()['teams'] if x['id'] == team_id][0]
    team_name = f'{team_info["location"]} {team_info["nickname"]}'

    # Get roster info
    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?forTeamId={team_id}&view=mRoster')
    roster = response.json()['teams'][0]['roster']['entries']

    # Get free agent info
    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?&view=kona_player_info',
                            headers={'x-fantasy-filter': json.dumps({"players": {"filterStatus": {"value": ["FREEAGENT", "WAIVERS"]}}})})
    free_agents = response.json()['players']

    # Organize Free Agents by position
    free_agent_dict = {position_dict[position]: [] for position in position_dict}

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
        team_player = {'id': player['playerId'],
                       'lineup_slot': lineup_dict[player['lineupSlotId']],
                       'name': player['playerPoolEntry']['player']['fullName'],
                       'team': player['playerPoolEntry']['player']['proTeamId'],
                       'position': position_dict[player['playerPoolEntry']['player']['defaultPositionId']],
                       'status': player['playerPoolEntry']['player']['injured'],
                       'tier': 'Not Ranked'}

        for tier in tiers[team_player['position']]:
            # Change the name of the DST team to match the source (ie. Rams D/ST to Los Angeles Rams)
            if team_player['position'] == 'D/ST':
                name = team_ids[team_player['team']]
            else:
                name = team_player['name']

            if name in tier[1]:
                team_player['tier'] = tier[0]

        # Set the lineup order values
        team_player['lineup_order'] = lineup_order[team_player['lineup_slot']]

        roster_dict[team_player['id']] = team_player

    # Reorder the dictionary to appear in proper lineup order to match ESPN
    lst = sorted(roster_dict, key=lambda x: (roster_dict[x]['lineup_order']))
    roster_dict = {k: roster_dict[k] for k in lst}

    # Match free agents with tiers
    for player in free_agents:
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
                free_agent_dict[temp['position']].append(temp)

    # Reorder the dictionaries by tier so they can be displayed in ascending order
    ordered_players = {}
    for position, value in free_agent_dict.items():
        ordered_players[position] = sorted(value, key=itemgetter('tier'))

    context = {'team_name': team_name,
               'roster': roster_dict,
               'free_agents': ordered_players}

    return render(request, 'tiers/view_team.html', context)


def view_matchup(request, team_id, league_id, scoring='standard', year=season):
    # Get the current matchup period to find team's opponent
    response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?view=mMatchupScore')
    matchup_id = response.json()['status']['currentMatchupPeriod']

    matchup = [x for x in response.json()['schedule'] if ((x['matchupPeriodId'] == matchup_id) and
                                                          ((x['home']['teamId'] == team_id) or
                                                           (x['away']['teamId'] == team_id)))][0]

    if matchup['home']['teamId'] == team_id:
        opponent_id = matchup['away']['teamId']
    else:
        opponent_id = matchup['home']['teamId']

    teams = {'team': team_id,
             'opponent': opponent_id}

    # Loop through teams to get info and rosters
    team_info = {}
    for key, value in teams.items():
        response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}')
        team_info[key] = {'team_id': value}
        info = [x for x in response.json()['teams'] if x['id'] == value][0]
        team_info[key]['team_name'] = f'{info["location"]} {info["nickname"]}'

        # Get roster info
        response = requests.get(f'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}?forTeamId={value}&view=mRoster')
        team_info[key]['roster'] = response.json()['teams'][0]['roster']['entries']

    # Get tiers for all positions
    tiers = {}
    for position_id, position_name in position_dict.items():
        if position_name == 'D/ST':
            position_name = 'DST'

        tiers[position_name] = get_tiers(scoring, position_name)

    # Update DST to D/ST
    tiers['D/ST'] = tiers.pop('DST')

    # For team and opponent, match players with tiers
    for team, ids in teams.items():
        roster_dict = {}
        for player in team_info[team]['roster']:
            team_player = {'id': player['playerId'],
                           'lineup_slot': lineup_dict[player['lineupSlotId']],
                           'name': player['playerPoolEntry']['player']['fullName'],
                           'team': player['playerPoolEntry']['player']['proTeamId'],
                           'position': position_dict[player['playerPoolEntry']['player']['defaultPositionId']],
                           'status': player['playerPoolEntry']['player']['injured'],
                           'tier': 'Not Ranked'}

            for tier in tiers[team_player['position']]:
                # Change the name of the DST team to match the source (ie. Rams D/ST to Los Angeles Rams)
                if team_player['position'] == 'D/ST':
                    name = team_ids[team_player['team']]
                else:
                    name = team_player['name']

                if name in tier[1]:
                    team_player['tier'] = tier[0]

            # Set the lineup order values
            team_player['lineup_order'] = lineup_order[team_player['lineup_slot']]

            roster_dict[team_player['id']] = team_player

            # Reorder the dictionary to appear in proper lineup order to match ESPN
            lst = sorted(roster_dict, key=lambda x: (roster_dict[x]['lineup_order']))
            roster_dict = {k: roster_dict[k] for k in lst}

        # Reassign roster in team_info dict to players with tiers
        team_info[team]['roster'] = roster_dict

    context = {'team_info': team_info,
               'roster': team_info['team'],
               'opponent': team_info['opponent']
               }

    return render(request, 'tiers/view_matchup.html', context)


def view_tiers(request, scoring):
    all_positions = {}
    # Show scoring for all positions
    for position_id, position_name in position_dict.items():
        if position_name == 'D/ST':
            position_name = 'DST'

        all_positions[position_name] = get_tiers(scoring, position_name)

    # Update DST to D/ST
    all_positions['D/ST'] = all_positions.pop('DST')

    # Make a separate dictionary for each tier for each position
    for position, tier_list in all_positions.items():
        tier_dict = {position: []}
        for tier in tier_list:
            tier_dict[position].append({tier[0]: tier[1]})

        all_positions[position] = tier_dict[position]

    context = {'tiers': all_positions,
               'scoring': scoring}

    return render(request, 'tiers/tiers.html', context)


# Gets the list of tiers from borischen.co based on the scoring type and the position
def get_tiers(scoring, position):
    # For QB, K, and DST positions, the scoring is standard
    if (scoring == 'standard') or (position in ['QB', 'K', 'DST']):
        with urllib.request.urlopen(tier_url.replace('{p}', position).replace('{s}', '')) as url:
            tiers = url.read().decode('utf-8').rstrip().split('\n')
    # Need to specify the scoring if the position is not QB, K, or DST
    else:
        with urllib.request.urlopen(tier_url.replace('{p}', position).replace('{s}', f'-{scoring}')) as url:
            tiers = url.read().decode('utf-8').rstrip().split('\n')

    tier_list = []
    for tier in tiers:
        # Split tier into tier name and players
        tier = tier.split(': ')
        tier_list.append(tier)

    return tier_list
