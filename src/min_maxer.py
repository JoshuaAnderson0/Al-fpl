from typing import TypeVar, List, Tuple, Callable, Generic
from datetime import datetime


T = TypeVar('T')
CURRENT_WEEK = datetime.now().isocalendar().week


class MinMaxer(Generic[T]):
    def __init__(self,
                 next_move_func: Callable[[List[T]], List[T]], 
                 eval_func: Callable[[List[T]], float],
                 hash_func: Callable[[List[T]], str] = lambda x: str(x)):
        self.next_move_func = next_move_func
        self.eval_func = eval_func
        self.hash_func = hash_func
        self.nodes_memo = []

    def solve(self, max_depth: int) -> List[T]:
        return self.search_tree([], self.next_move_func([]), max_depth)

    def search_tree(self,
                    current_tree: List[T],
                    possible_nodes: List[T],
                    depth: int,
                    beta: float = float('-inf')) -> T:
        if depth == 0 or len(possible_nodes) == 0:
            return current_tree

        result = None
        local_best = float('-inf')
        local_best_index = 0
        for i, node in enumerate(possible_nodes):
            new_tree = current_tree + [node]
            if self.hash_func(new_tree) in self.nodes_memo:
                return []
            self.nodes_memo.append(self.hash_func(new_tree))

            score = self.eval_func(new_tree)
            if score > local_best:
                local_best = score
                local_best_index = i

            if score <= beta:
                continue
            beta = score

            result = self.search_tree(new_tree, self.next_move_func(new_tree), depth - 1, beta)

        if result is None:
            new_tree = current_tree + [possible_nodes[local_best_index]]
            return self.search_tree(new_tree, self.next_move_func(new_tree), depth - 1, beta)
        return result
