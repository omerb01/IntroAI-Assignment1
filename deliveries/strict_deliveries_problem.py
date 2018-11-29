from framework.graph_search import *
from framework.ways import *
from .map_problem import MapProblem
from .deliveries_problem_input import DeliveriesProblemInput
from .relaxed_deliveries_problem import RelaxedDeliveriesState, RelaxedDeliveriesProblem

from typing import Set, FrozenSet, Optional, Iterator, Tuple, Union


class StrictDeliveriesState(RelaxedDeliveriesState):
    """
    An instance of this class represents a state of the strict
     deliveries problem.
    This state is basically similar to the state of the relaxed
     problem. Hence, this class inherits from `RelaxedDeliveriesState`.

    TODO:
        If you believe you need to modify the state for the strict
         problem in some sense, please go ahead and do so.
    """
    pass


class StrictDeliveriesProblem(RelaxedDeliveriesProblem):
    """
    An instance of this class represents a strict deliveries problem.
    """

    name = 'StrictDeliveries'

    def __init__(self, problem_input: DeliveriesProblemInput, roads: Roads,
                 inner_problem_solver: GraphProblemSolver, use_cache: bool = True):
        super(StrictDeliveriesProblem, self).__init__(problem_input)
        self.initial_state = StrictDeliveriesState(
            problem_input.start_point, frozenset(), problem_input.gas_tank_init_fuel)
        self.inner_problem_solver = inner_problem_solver
        self.roads = roads
        self.use_cache = use_cache
        self._init_cache()

    def _init_cache(self):
        self._cache = {}
        self.nr_cache_hits = 0
        self.nr_cache_misses = 0

    def _insert_to_cache(self, key, val):
        if self.use_cache:
            self._cache[key] = val

    def _get_from_cache(self, key):
        if not self.use_cache:
            return None
        if key in self._cache:
            self.nr_cache_hits += 1
        else:
            self.nr_cache_misses += 1
        return self._cache.get(key)

    def expand_state_with_costs(self, state_to_expand: GraphProblemState) -> Iterator[Tuple[GraphProblemState, float]]:
        """
        TODO: implement this method!
        This method represents the `Succ: S -> P(S)` function of the strict deliveries problem.
        The `Succ` function is defined by the problem operators as shown in class.
        The relaxed problem operators are defined in the assignment instructions.
        It receives a state and iterates over the successor states.
        Notice that this is an *Iterator*. Hence it should be implemented using the `yield` keyword.
        For each successor, a pair of the successor state and the operator cost is yielded.
        """
        assert isinstance(state_to_expand, StrictDeliveriesState)
        UNREACHABLE_NODE = -1

        # Iterate over all the other possible stop points.
        for stop in self.possible_stop_points - state_to_expand.dropped_so_far:
            # Check if the current stop isn't the state to expand.
            if stop == state_to_expand.current_location:
                continue

            cache_key = (state_to_expand.current_location.index, stop.index)
            operator_cost = self._get_from_cache(cache_key)

            # we haven't calculated the distance from these two stops
            if operator_cost is None:
                new_map_prob = MapProblem(self.roads, state_to_expand.current_location.index, stop.index)
                restult_node = self.inner_problem_solver.solve_problem(new_map_prob).final_search_node
                # can't reach the desired stop.
                if restult_node is None:
                    operator_cost = UNREACHABLE_NODE
                else:
                    operator_cost = restult_node.cost
                # insert to cache
                self._insert_to_cache(cache_key, operator_cost)

            # unreachable stop from current location, continue.
            if operator_cost == UNREACHABLE_NODE:
                continue

            # Create the successor state if the fuel is enough to reach that point.
            if state_to_expand.fuel_as_int >= operator_cost * 1000000:  # fuel as int returns a larger unit by 1000000
                if stop in self.gas_stations:
                    successor_state = StrictDeliveriesState(stop, state_to_expand.dropped_so_far,
                                                             self.gas_tank_capacity)
                    yield successor_state, operator_cost
                elif stop in self.drop_points:
                    # Create new dropped so far set with the new drop point.
                    new_dropped_so_far = set()
                    for j in state_to_expand.dropped_so_far:
                        new_dropped_so_far.add(j)
                    new_dropped_so_far.add(stop)
                    successor_state = StrictDeliveriesState(stop, new_dropped_so_far
                                                            , state_to_expand.fuel - operator_cost)
                    yield successor_state, operator_cost
                else:
                    raise Exception("Stop is not gas station or drop point :'( ")

    def is_goal(self, state: GraphProblemState) -> bool:
        """
        This method receives a state and returns whether this state is a goal.
        TODO: implement this method!
        """
        assert isinstance(state, StrictDeliveriesState)

        return self.drop_points == state.dropped_so_far
