import asyncio
import aiohttp

from typing import Dict

from api import API
from player import Player
from player_types import *
from team import Team
from min_maxer import MinMaxer


MANAGER_BUDGET = 100_000_000


async def get_all_players_async(session: aiohttp.ClientSession, bootstrap: Dict[str, object]) -> [Player]:
    tasks = []
    for index in range(1, 610):
        tasks.append(asyncio.ensure_future(API.get_player_data_async(session, index, bootstrap)))

    players = await asyncio.gather(*tasks)
    return [player for player in players if player is not None]


def get_all_teams_from_players(players: [Player]) -> [Team]:
    teams = {}
    for player in players:
        team_id = player.team_id

        if team_id not in teams:
            teams[team_id] = Team(team_id, [], [])

        teams[team_id].players.append(player)
        if player.history_len > 0 and player.minutes_played / player.history_len > 360:
            teams[team_id].regulars.append(player)

    return list(teams.values())


def validate_team_pick(team: [Player]) -> bool:
    player_types = {1: 0, 2: 0, 3: 0, 4: 0}
    predicted_budget = MANAGER_BUDGET

    for player in team:
        player_types[player.player_type] += 1
        predicted_budget -= player.cost

    if predicted_budget < 0:
        return False

    for player_type in player_types:
        if player_types[player_type] > get_allowed_max_of_type(player_type):
            return False
    return True


async def main_async():
    async with aiohttp.ClientSession() as session:
        print('Getting data for all players')
        bootstrap = await API.get_bootstrap_data_async(session)
        players   = await get_all_players_async(session, bootstrap)

    # teams = get_all_teams_from_players(players)
    print('Choosing best team of members')

    min_maxer = MinMaxer(
        lambda p: p.roi,
        15,
        validate_team_pick
    )

    types = {
        1: [],
        2: [],
        3: [],
        4: []
    }
    for player in players:
        types[player.player_type].append(player)
    for key in types.keys():
        print(len(types[key]))

    # best_team = await min_maxer.get_best_permutation_async(players)
    # 
    # if len(best_team) == 0:
    #     print('something went wrong while choosing the best team')
    #     return
    # 
    # print('the best team is:')
    # for player in best_team:
    #     print(f'\n{player.name} - {get_type_name(player.player_type)}')

if __name__ == '__main__':
    asyncio.run(main_async())
