import copy
import random
import typing

from Search.alt_state import Gstate
from TrafficSimulator.window import *
from TrafficSimulator.Setups.two_way_intersection import *

INIT_SOLUTION_5 = [[0, 0, 0, 1, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 1],
                   [1, 0, 0, 0, 0],
                   [0, 1, 0, 0, 0], [0, 0, 0, 0, 0]]
INIT_SOLUTION_3 = [[0, 0, 0], [0, 0, 1], [1, 0, 0],
                   [0, 1, 0]]
INIT_SOLUTION_4 = [[0, 0, 0, 1], [0, 0, 1, 0], [0, 0, 0, 0],
                   [1, 0, 0, 0], [0, 1, 0, 0], [1, 0, 0, 1]]

INIT_SOLUTION_6 = [[0, 0, 0, 1, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 0],
                   [1, 0, 0, 0, 0, 0],
                   [0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0],
                   [1, 0, 0, 1, 0, 0]]
INI_SOLS = {3: INIT_SOLUTION_3, 4: INIT_SOLUTION_4, 5: INIT_SOLUTION_5,
            6: INIT_SOLUTION_6}
PARTITION_INDEX = 2


def take_eval(elem):
    """
    Helper function for sorting, returns the eval attribute of an object
    """
    return elem.eval


class Solution:
    """
    A Solution is an object that contains a schedule and its evaluated score
    The solution is a list of actions, to commit on the simulation
    """

    def __init__(self, solution):
        """

        :param solution:
        """
        self.solution = solution
        self.eval = 0

    def evaluate(self, state: Gstate):
        """
        Evaluates purposed solution on the given state
        :param state: a "snapshot" of the current simulation
        """
        state.penalty = 1
        for action in self.solution:
            state.apply_action(action)
            if state.abrupt():
                self.eval = 0
                break
        if not state.abrupt():
            # While running the solution on the state we calculate a score
            # and penalty
            self.eval = state.score * state.penalty


def check_unavoidable(state: Gstate):
    """
    Checks if there will be an unavoidable collision
    """
    cs = copy.deepcopy(state)
    cs.apply_action(0)
    if cs.abrupt():
        return True
    return False


class Genetics:
    """
    """

    def __init__(self, solution_length, action_space):
        """

        :param solution_length: a number ranges from 3-6
        :param action_space: the action space for the mutation
        """
        self.possible_solutions = []
        self.solution_length = solution_length
        self.action_space = action_space

    def generate_innit_solution(self) -> None:
        """
        Creates Initial solution list, after many testing we realized there
        should be a fixed list of simple schedules
        """
        for c in INI_SOLS[self.solution_length]:
            sol = Solution(c)
            self.possible_solutions.append(sol)

    def run_eval(self, state: Gstate) -> None:
        """
        Runs evaluation on each of the possible solution
        :param state: a given state of the running simulation
        """
        for sol in self.possible_solutions:
            cs = copy.deepcopy(state)
            sol.evaluate(cs)

    def cross_over(self) -> None:
        """
        applies the cross over process in the genetic algorithm
        """
        self.possible_solutions.sort(key=take_eval)
        new_sol_chain = []
        for i in range(0, len(self.possible_solutions) - 1, 2):
            new_chain = self.possible_solutions[i].solution[0:PARTITION_INDEX] + \
                        self.possible_solutions[i + 1].solution[
                        PARTITION_INDEX:self.solution_length]
            new_chain2 = self.possible_solutions[i + 1].solution[0:PARTITION_INDEX] + \
                         self.possible_solutions[i].solution[
                         PARTITION_INDEX:self.solution_length]
            new_sol_chain.append(new_chain)
            new_sol_chain.append(new_chain2)
        self.possible_solutions = []
        for c in new_sol_chain:
            sol = Solution(c)
            self.possible_solutions.append(sol)

    def mutate(self) -> None:
        """
        Creates a mutation by probability to the possible solution
        """
        e = 0
        for sol in self.possible_solutions:
            e = random.random()
            if e > 0.7:
                sol.solution[
                    random.randrange(self.solution_length)] = random.choice(
                    self.action_space)

    def failed_fit(self, bar) -> bool:
        """
        checks if there are no solutions that pass the minimum criteria to
        be a valid solution
        :return: True or False
        """
        for s in self.possible_solutions:
            if s.eval > bar:
                return False
        return True

    def best_of(self) -> typing.List:
        """
        :return: The best solution out of all possible solution
        """
        return (max(self.possible_solutions, key=take_eval)).solution

    def pick(self, state) -> typing.List:
        """
        picks the best list of actions to commit on the running simulation
        :param state: the current state of the running simulation
        :return:
        """
        min_optimal = state.min_optimal_score()
        self.possible_solutions = []
        if state.is_empty() or check_unavoidable(state):
            return [0]
        self.generate_innit_solution()
        self.run_eval(state)
        while self.failed_fit(min_optimal):
            self.cross_over()
            self.mutate()
            self.run_eval(state)
        return self.best_of()
