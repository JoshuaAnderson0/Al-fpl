from typing import Dict
from dataclasses import dataclass
from datetime import datetime


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
    player_type: int

    @property
    def roi(self) -> float:
        return self.total_points / self.cost if self.cost != 0 else 0

    @classmethod
    def from_json(cls, player_id: int, data: Dict[str, object], bootstrap: Dict[str, object]) -> 'Player':
        fixture: [Dict[str, object]] = data.get('fixtures', [])

        if len(fixture) == 0:
            return cls(0, '', 0, 0, 0, [], 0, 0, 0)

        games_past: [Dict[str, object]] = data.get('history', [])
        history_past: [Dict[str, object]] = data.get('history_past', [])
        player_details: [Dict[str, object]] = bootstrap.get('elements', [])[player_id]

        history_points  = sum([i.get('total_points', 0) for i in history_past])
        current_points  = sum([i.get('total_points', 0) for i in games_past])
        history_minutes = sum([i.get('minutes', 0) for i in history_past])
        current_minutes = sum([i.get('minutes', 0) for i in games_past])

        name           = player_details.get('first_name', '') + ' ' + player_details.get('second_name', '')
        total_points   = history_points + current_points
        minutes_played = history_minutes + current_minutes
        future_games   = [i.get('kickoff_time', '') for i in fixture]
        team_id        = fixture[0].get('team_h', 0) if fixture[0].get('is_home') else fixture[0].get('team_a', 0)
        cost           = player_details.get('now_cost', 0)
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
            player_type
        )
