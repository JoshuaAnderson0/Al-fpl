from dataclasses import dataclass
from player import Player


@dataclass
class Team:
    id: int
    players: [Player]
    regulars: [Player]

    @property
    def average_roi(self) -> float:
        return sum([player.roi for player in self.regulars]) / len(self.regulars)

    @property
    def team_roi(self) -> float:
        return len(self.regulars) - self.average_roi
