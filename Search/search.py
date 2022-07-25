from typing import List, TypeVar, Dict

import util

State = TypeVar("State")  # State
Triplet = TypeVar("Triplet")  # (State, Action, Action_Cost)
Action = TypeVar("Action")  # Action object


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def get_start_state(self) -> State:
        """
        Returns the start state for the search problem
        """
        pass

    def is_goal_state(self, state: State) -> bool:
        """
        state: Search state

        Returns True if and only if the state is a valid goal state
        """
        pass

    def get_successors(self, state: State) -> List[State]:
        """
        state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        pass

    def get_cost_of_actions(self, actions: List[Action]):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        pass


# 2.1   DFS:                        Expanded nodes: 63,     score: 17   # 0.1 seconds   #was 0.4
# 2.2   BFS:                        Expanded nodes: 1655,   score: 17   # 1.6 seconds   #was 4
# 2.1   DFS Pacman:                 Expanded nodes: 144,    cost: 130
# 2.2   BFS Pacman:                 Expanded nodes: 267,    cost: 68
# 3.1   BlokusCornerProblem BFS:    Expanded nodes: 890,    score: 17   # 3.4 seconds   #was 9
# 3.2   UCS 1st:                    Expanded nodes: 21871,  score: 17   # 39 seconds    #was 93
# 3.2   UCS 2nd:                    Expanded nodes: 38733,  score: 13   # 117 seconds   #was 241
# 3.3   A*:                         Expanded nodes: 21871,  score: 17   # 39 seconds    #was 93
# 4.1   CornerHeuristic A*:         Expanded nodes: 1988,   score: 17   # 5.9 seconds   #was 10
# 5.1   BlokusCoverProblem A*:      Expanded nodes: 6445,   score: 7    # 106 seconds   #was 182
# 5.2   CoverHeuristic A*:          Expanded nodes: 590,    score: 8    # 22/79 seconds #was 134nodes/22sec
# 6.1   ClosetPoint:                Expanded nodes: 11,     score: 9    # 2.1 seconds   #was 1
# 6.1   ClosetPoint:                Expanded nodes: 23,     score: 9    # 7.9 seconds   #was 6.8
# 6.2   MiniContest:

def depth_first_search(problem: SearchProblem) -> List[Action]:
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches
    the goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.get_start_state().state)
    print("Is the start a goal?", problem.is_goal_state(problem.get_start_state()))
    print("Start's successors:", problem.get_successors(problem.get_start_state()))
    """
    return fs_search_template(problem, util.Stack())


def breadth_first_search(problem: SearchProblem) -> List[Action]:
    """
    Search the shallowest nodes in the search tree first.
    """
    return fs_search_template(problem, util.Queue())


def fs_search_template(problem: SearchProblem, fringe) -> List[Action]:
    root: State = problem.get_start_state()
    if problem.is_goal_state(root):
        return []
    parents_dict: Dict = {root: (None, None)}  # {State: (Action, Parent_State)}
    fringe.push(root)
    while not fringe.is_empty():
        parent = fringe.pop()
        for state, action, cost in problem.get_successors(parent):
            if state not in parents_dict:
                parents_dict[state] = (action, parent)
                if problem.is_goal_state(state):
                    return path_to_goal(parents_dict, state)
                fringe.push(state)


def null_heuristic(state: State, problem: SearchProblem = None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def uniform_cost_search(problem: SearchProblem, heuristic=null_heuristic,
                        return_goal_state: bool = False):
    """
    Search the node of the least total cost first.
    """
    return priority_search_template(problem, heuristic, return_goal_state)


def a_star_search(problem: SearchProblem, heuristic=null_heuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """
    return priority_search_template(problem, heuristic)


def priority_search_template(problem: SearchProblem, heuristic=null_heuristic,
                             return_goal_state: bool = False):
    root: State = problem.get_start_state()
    if problem.is_goal_state(root):
        return []
    pq = util.PriorityQueue()
    parents_dict: Dict = {root: (None, None, 0)}  # {State: (Action, Parent_State, Cost)}
    pq.push(root, 0)
    while not pq.is_empty():
        parent = pq.pop()
        if problem.is_goal_state(parent):
            if return_goal_state:
                return parent, path_to_goal(parents_dict, parent)
            else:
                return path_to_goal(parents_dict, parent)
        priority_add_children(parent, problem, parents_dict, pq, heuristic)


def priority_add_children(parent: State, problem: SearchProblem,
                          parents_dict: Dict, pq: util.PriorityQueue(), heuristic) -> None:
    for state, action, cost in problem.get_successors(parent):
        if state not in parents_dict:
            cost += parents_dict[parent][2]
            if heuristic != null_heuristic:
                cost += heuristic(state, problem)
            pq.push(state, cost)
            parents_dict[state] = (action, parent, cost)


def path_to_goal(parents_dict: Dict, current: State) -> List[Action]:
    actions = []
    while parents_dict.get(current):  # {State: (Action, Parent_State, *)}
        action, parent = parents_dict[current][0], parents_dict[current][1]
        if not action:  # reached root
            actions.reverse()
            return actions
        actions.append(action)
        current = parent


# Abbreviations
bfs = breadth_first_search
dfs = depth_first_search
astar = a_star_search
ucs = uniform_cost_search
