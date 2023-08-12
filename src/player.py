from typing import Dict
from dataclasses import dataclass
from datetime import datetime


def get_sum_of_history_points(
        history: [Dict[str, object]], 
        season_history: [Dict[str, object]], 
        key: str, 
        default_val: int) -> int:
    return (
            sum([i.get(key, default_val) for i in history]) + 
            sum([i.get(key, default_val) for i in season_history])
    )


@dataclass
class Player:
    id: int
    name: str
    total_points: int
    minutes_played: int
    history_len: int
    future_games: [datetime]
    team_id: int
    cost: int
    red_cards: int
    yellow_cards: int
    player_type: int

    @property
    def roi(self) -> float:
        return self.total_points / self.cost if self.cost != 0 else 0

    @classmethod
    def from_json(cls, player_id: int, data: Dict[str, object], bootstrap: Dict[str, object]) -> 'Player':
        fixture: [Dict[str, object]] = data.get('fixtures', [])

        if len(fixture) == 0:
            return cls(0, '', 0, 0, 0, [], 0, 0, 0, 0, 0)

        games_past: [Dict[str, object]] = data.get('history', [])
        history_past: [Dict[str, object]] = data.get('history_past', [])
        player_details: [Dict[str, object]] = bootstrap.get('elements', [])[player_id]

        name           = player_details.get('first_name', '') + ' ' + player_details.get('second_name', '')
        total_points   = get_sum_of_history_points(games_past, history_past, 'total_points', 0)
        minutes_played = get_sum_of_history_points(games_past, history_past, 'minutes', 0) 
        red_cards      = get_sum_of_history_points(games_past, history_past, 'red_cards', 0)
        yellow_cards   = get_sum_of_history_points(games_past, history_past, 'yellow_cards', 0)
        future_games   = [i.get('kickoff_time', '') for i in fixture if i.get('kickoff_time') is not None]
        team_id        = fixture[0].get('team_h', 0) if fixture[0].get('is_home') else fixture[0].get('team_a', 0)
        cost           = player_details.get('now_cost', 0) / 10
        player_type    = player_details.get('element_type', 0)

        return cls(
            player_id,
            name,
            total_points,
            minutes_played,
            len(history_past),
            future_games,
            team_id,
            cost,
            red_cards,
            yellow_cards,
            player_type
        )
