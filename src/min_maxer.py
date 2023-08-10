import asyncio

from typing import Dict, List

from player import Player


class MinMaxer:
    def __init__(self, score_func: lambda player: float, max_length: int, validation_func: lambda players: bool):
        self.score_func = score_func
        self.max_length = max_length
        self.validation_func = validation_func
        self.memo: Dict[str, List[Player]] = {}

    async def get_best_permutation_async(self, players: List[Player], batch_size: int = 60) -> List[Player]:
        self.memo = {}

        index = 0
        await self.get_best_permutation_with_head_async([players[0]], players[1:])
        # while True:
        #     tasks = []
        #     for i in range(batch_size):
        #         if index >= len(players):
        #             continue
        # 
        #         head = [players[index]]
        #         remaining = [player for player in players if player not in head]
        #         tasks.append(asyncio.ensure_future(self.get_best_permutation_with_head_async(head, remaining)))
        #         index += 1
        # 
        #     await asyncio.gather(*tasks)
        #     tasks = []
        #     print(index)
        # 
        #     if index >= len(players):
        #         break

        return []

    async def get_best_permutation_with_head_async(self, players: List[Player], remaining: List[Player]):
        cached_key = ''.join(sorted([player.name for player in players]))
        if cached_key in self.memo:
            return
        self.memo[cached_key] = players

        for player in remaining:
            new_team = [*players, player]
            if self.validation_func(new_team):
                new_remaining = [player for player in remaining if player not in new_team]
                await self.get_best_permutation_with_head_async(new_team, new_remaining)
            else:
                break
