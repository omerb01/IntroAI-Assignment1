from .graph_problem_interface import *
from .best_first_search import BestFirstSearch
from typing import Optional
import numpy as np


class GreedyStochastic(BestFirstSearch):
    def __init__(self, heuristic_function_type: HeuristicFunctionType,
                 T_init: float = 1.0, N: int = 5, T_scale_factor: float = 0.95):
        # GreedyStochastic is a graph search algorithm. Hence, we use close set.
        super(GreedyStochastic, self).__init__(use_close=True)
        self.heuristic_function_type = heuristic_function_type
        self.T = T_init
        self.N = N
        self.T_scale_factor = T_scale_factor
        self.solver_name = 'GreedyStochastic (h={heuristic_name})'.format(
            heuristic_name=heuristic_function_type.heuristic_name)

    def _init_solver(self, problem: GraphProblem):
        super(GreedyStochastic, self)._init_solver(problem)
        self.heuristic_function = self.heuristic_function_type(problem)

    def _open_successor_node(self, problem: GraphProblem, successor_node: SearchNode):
        """
        TODO: implement this method!
        """

        # check if node is not in open and not in close, if so put it in open.
        if not self.open.has_state(successor_node.state) and not self.close.has_state(successor_node.state):
            self.open.push_node(successor_node)

    def _calc_node_expanding_priority(self, search_node: SearchNode) -> float:
        """
        TODO: implement this method!
        Remember: `GreedyStochastic` is greedy.
        """

        return self.heuristic_function.estimate(search_node.state)

    def _extract_next_search_node_to_expand(self) -> Optional[SearchNode]:
        """
        Extracts the next node to expand from the open queue,
         using the stochastic method to choose out of the N
         best items from open.
        TODO: implement this method!
        Use `np.random.choice(...)` whenever you need to randomly choose
         an item from an array of items given a probabilities array `p`.
        You can read the documentation of `np.random.choice(...)` and
         see usage examples by searching it in Google.
        Notice: You might want to pop min(N, len(open) items from the
                `open` priority queue, and then choose an item out
                of these popped items. The other items have to be
                pushed again into that queue.
        """

        if self.open.is_empty():
            return None

        size_to_extract = min(self.N, len(self.open))
        # check if size of open is smaller than N.

        h = self.heuristic_function.estimate

        # put all min(N,sizeof(open)) nodes in a list called x (just like in the example)
        x = []
        for i in range(size_to_extract):
            node = self.open.pop_next_node()
            x.append(node)
        min_node = x[0]

        # we might have reached out goal and the heuristic function will return 0
        if h(min_node.state) == 0:
            node_to_expand = min_node
        else:
            # calc the probability list for each heuristic value.
            p = []
            sum = 0
            for x_node in x:
                sum += ((h(x_node.state) / h(min_node.state)) ** ((-1) / self.T))

            for x_node in x:
                probability = ((h(x_node.state) / h(min_node.state)) ** ((-1) / self.T)) / sum
                p.append(probability)

            # choose randomly
            node_to_expand = np.random.choice(x, size=None, p=p)

        # pushing un-chosen nodes back to the open list
        for x_node in x:
            if x_node.state != node_to_expand.state:
                self.open.push_node(x_node)

        # put chosen node in close
        if self.use_close:
            self.close.add_node(node_to_expand)

        # decrese T by 0.95
        self.T *= self.T_scale_factor
        return node_to_expand
