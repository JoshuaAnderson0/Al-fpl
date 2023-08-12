import asyncio
import aiohttp

from datetime import datetime
from typing import Dict, List, Callable

from api import API
from player import Player
from player_types import *
from team import Team
from min_maxer import MinMaxer


MANAGER_BUDGET = 100
CURRENT_WEEK = datetime.now().isocalendar().week


async def get_all_players_async(session: aiohttp.ClientSession, bootstrap: Dict[str, object]) -> [Player]:
    tasks = []
    for index in range(1, 610):
        tasks.append(asyncio.ensure_future(API.get_player_data_async(session, index, bootstrap)))

    players = await asyncio.gather(*tasks)
    return [player for player in players if player is not None]


def validate_team_pick(team: [Player]) -> bool:
    player_types = {1: 0, 2: 0, 3: 0, 4: 0}
    teams = {}
    predicted_budget = MANAGER_BUDGET

    for player in team:
        player_types[player.player_type] += 1

        if player.team_id not in teams:
            teams[player.team_id] = 0
        teams[player.team_id] += 1

        predicted_budget -= player.cost

    if (predicted_budget >= 0 and
        not any(v > get_allowed_max_of_type(k) for k, v in player_types.items()) and
        not any(x > 3 for x in teams.values())):
        return True
    return False


def make_legal_moves_functor(players: [Player]) -> Callable[[List[Player]], List[Player]]:
    average_roi = sum([player.roi for player in players]) / len(players)
    return lambda team: [
        player for player in players if (validate_team_pick(team + [player]) and
                                         player not in team and
                                         player.roi >= average_roi)
    ]


def evaluate_team(team: [Player]) -> float:
    return sum(
        (
            sum(player.roi for game in player.future_games if datetime.strptime(game, "%Y-%m-%dT%H:%M:%SZ").isocalendar().week == CURRENT_WEEK)
            - (player.roi * player.red_cards)
            # - (player.roi * player.yellow_cards * 0.25)
            - player.cost
        )
        for player in team
    )


async def main_async():
    global MANAGER_BUDGET

    async with aiohttp.ClientSession() as session:
        print('Getting data for all players')
        bootstrap = await API.get_bootstrap_data_async(session)
        players   = await get_all_players_async(session, bootstrap)

    players = sorted(players, key=lambda x: x.roi, reverse=True)

    # Blacklist these players because for some reason they don't actually appear on the fpl website
    players = [player for player in players if player.name not in ["Ellis Simms", "Pierre-Emerick Aubameyang", "Trevoh Chalobah", "Mads Bidstrup", "Halil Dervişoğlu", "Antwoine Hackford"]]

    print('Choosing best team of members')

    min_maxer = MinMaxer(
        make_legal_moves_functor(players),
        evaluate_team
    )
    best_team = min_maxer.solve(15)

    for player in best_team:
        print(player.name)

if __name__ == '__main__':
    asyncio.run(main_async())
