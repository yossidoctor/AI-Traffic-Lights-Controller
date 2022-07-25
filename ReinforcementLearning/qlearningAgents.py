import random

import util
from learningAgents import ReinforcementAgent


class QLearningAgent(ReinforcementAgent):
    """
      Q-Learning Agent
      Functions you should fill in:
        - getQValue
        - getAction
        - getValue
        - getPolicy
        - update
      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)
      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions
          for a state
    """

    def __init__(self, **args):
        """You can initialize Q-values here..."""
        ReinforcementAgent.__init__(self, **args)

        self.q_values = util.Counter()

    def get_qvalue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen
          a state or (state,action) tuple
        """
        return self.q_values[(state, action)]

    def get_value(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        if not self.get_legal_actions(state):
            return 0

        action_vals = [self.get_qvalue(state, action) for action in self.get_legal_actions(state)]
        random.shuffle(action_vals)
        return max(action_vals)
        # best_action = self.getPolicy(state)
        # return self.getQValue(state, best_action)

    def get_policy(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        if not self.get_legal_actions(state):
            return None

        action_vals = [(action, self.get_qvalue(state, action)) for action in self.get_legal_actions(state)]
        max_val = max([self.get_qvalue(state, action) for action in self.get_legal_actions(state)])
        best_actions = [action for action, val in action_vals if val == max_val]
        return random.choice(best_actions)

        # actions = list(self.get_legal_actions(state))
        # random.shuffle(actions)
        # return max(actions, key=lambda action: self.getQValue(state, action))

    def get_action(self, state):
        """
          Compute the action to take in the current state. With
          probability self.Epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        if not self.get_legal_actions(state):
            return None

        explore = util.flip_coin(self.epsilon)

        if explore:
            legal_actions = self.get_legal_actions(state)
            return random.choice(legal_actions)

        return self.get_policy(state)

    def update(self, state, action, next_state, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here
          NOTE: You should never call this function,
          it will be called on your behalf
        """
        curr_q_val = self.q_values[(state, action)]
        self.q_values[(state, action)] = (1 - self.alpha) * curr_q_val + self.alpha * (
                reward + self.discount * self.get_value(next_state))

# class QLearningAgent(ReinforcementAgent):
#     """
#       Q-Learning Agent
#       Functions you should fill in:
#         - getQValue
#         - getAction
#         - getValue
#         - getPolicy
#         - update
#       Instance variables you have access to
#         - self.epsilon (exploration prob)
#         - self.alpha (learning rate)
#         - self.discount (discount rate)
#       Functions you should use
#         - self.get_legal_actions(state)
#           which returns legal actions
#           for a state
#     """
#     def __init__(self, **args):
#         "You can initialize Q-values here..."
#         ReinforcementAgent.__init__(self, **args)
#         self.Q = util.Counter()
#
#     def getQValue(self, state, action):
#         """
#           Returns Q(state,action)
#           Should return 0.0 if we have never seen
#           a state or (state,action) tuple
#         """
#         return self.Q[(state, action)]
#
#     def getValue(self, state):
#         """
#           Returns max_action Q(state,action)
#           where the max is over legal actions.  Note that if
#           there are no legal actions, which is the case at the
#           terminal state, you should return a value of 0.0.
#         """
#
#         legal_actions = self.get_legal_actions(state)
#         if not legalActions:
#             return 0.0
#
#         vals = []
#         for action in legalActions:
#             vals.append(self.getQValue(state, action))
#
#         random.shuffle(vals)
#         return max(vals)
#
#     def getPolicy(self, state):
#         """
#           Compute the best action to take in a state.  Note that if there
#           are no legal actions, which is the case at the terminal state,
#           you should return None.
#         """
#
#         legalActions = self.get_legal_actions(state)
#         if not legalActions:
#             return None
#
#         m = float('-inf')
#         for action in legal_actions:
#             val = self.getQValue(state, action)
#             if val == m:
#                 max_actions.append(action)
#             elif val > m:
#                 m = val
#                 max_actions = [action]
#
#         return random.choice(max_actions)
#
#     def get_action(self, state):
#         """
#           Compute the action to take in the current state.  With
#           probability self.epsilon, we should take a random action and
#           take the best policy action otherwise.  Note that if there are
#           no legal actions, which is the case at the terminal state, you
#           should choose None as the action.
#           HINT: You might want to use util.flip_coin(prob)
#           HINT: To pick randomly from a list, use random.choice(list)
#         """
#         # Pick Action
#
#         legal_actions = self.get_legal_actions(state)
#         if not legalActions:
#             return None
#
#         if util.flipCoin(self.epsilon):
#             return random.choice(legal_actions)
#
#         return self.getPolicy(state)
#
# def update(self, state, action, nextState, reward): """ The parent class calls this to observe a state = action =>
# nextState and reward transition. You should do your Q-Value update here NOTE: You should never call this function,
# it will be called on your behalf """ self.Q[(state, action)] += self.alpha * (reward + self.discount *
# self.getValue(nextState) - self.getQValue(state, action))


# class PacmanQAgent(QLearningAgent):
#     "Exactly the same as QLearningAgent, but with different default parameters"
#
#     def __init__(self, epsilon=0.05, gamma=0.8, alpha=0.2, numTraining=0, **args):
#         """
#         These default parameters can be changed from the pacman.py command line.
#         For example, to change the exploration rate, try:
#             python pacman.py -p PacmanQLearningAgent -a epsilon=0.1
#
#         alpha    - learning rate
#         epsilon  - exploration rate
#         gamma    - discount factor
#         numTraining - number of training episodes, i.e. no learning after these many episodes
#         """
#         args['epsilon'] = epsilon
#         args['gamma'] = gamma
#         args['alpha'] = alpha
#         args['numTraining'] = numTraining
#         self.index = 0  # This is always Pacman
#         QLearningAgent.__init__(self, **args)
#
#     def getAction(self, state):
#         """
#         Simply calls the getAction method of QLearningAgent and then
#         informs parent of action for Pacman.  Do not change or remove this
#         method.
#         """
#         action = QLearningAgent.getAction(self, state)
#         self.doAction(state, action)
#         return action
#
#
# class ApproximateQAgent(PacmanQAgent):
#     """
#        ApproximateQLearningAgent
#
#        You should only have to overwrite getQValue
#        and update.  All other QLearningAgent functions
#        should work as is.
#     """
#
#     def __init__(self, extractor='IdentityExtractor', **args):
#         self.featExtractor = util.lookup(extractor, globals())()
#         PacmanQAgent.__init__(self, **args)
#
#         self.weights = util.Counter()
#
#     def getQValue(self, state, action):
#         return self.weights * self.featExtractor.getFeatures(state, action)
#
#     def update(self, state, action, nextState, reward):
#         """
#            Should update your weights based on transition
#         """
#         features = self.featExtractor.getFeatures(state, action)  # {feature: value}
#         correction = reward + self.discount * self.getValue(nextState) - self.getQValue(state, action)
#
#         for feature in features:
#             self.weights[feature] += self.alpha * correction * features[feature]
#
#     def final(self, state):
#         "Called at the end of each game."
#         # call the super-class final method
#         PacmanQAgent.final(self, state)
#
#         # did we finish training?
#         if self.episodesSoFar == self.numTraining:
#             # you might want to print your weights here for debugging
#             "*** YOUR CODE HERE ***"
#             pass
