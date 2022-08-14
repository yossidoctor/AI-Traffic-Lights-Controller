import random


class QLearningAgent:
    def __init__(self, alpha, epsilon, discount, actions):
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.discount = float(discount)
        self.actions = actions
        self.q_values = {}

    def get_qvalue(self, state, action):
        if (state, action) not in self.q_values:
            return 0.0
        return self.q_values[(state, action)]

    def get_value(self, state):
        action_vals = [self.get_qvalue(state, action) for action in self.actions]
        random.shuffle(action_vals)
        return max(action_vals)

    def get_policy(self, state):
        """
          Compute the best action to take in a state. If there are no legal 
          actions, which is the case at the terminal state, returns None.
        """
        action_vals = [(action, self.get_qvalue(state, action)) for action in self.actions]
        max_val = max([self.get_qvalue(state, action) for action in self.actions])
        best_actions = [action for action, val in action_vals if val == max_val]
        return random.choice(best_actions)

    def get_action(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, takes a random action and
          take the best policy action otherwise. If there are
          no legal actions, which is the case at the terminal state, 
          chooses None as the action
        """
        r = random.random()

        if r < self.epsilon:
            return random.choice(self.actions)

        return self.get_policy(state)

    def update(self, state, action, next_state, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
        """
        curr_q_val = self.get_qvalue(state, action)
        self.q_values[(state, action)] = (1 - self.alpha) * curr_q_val + self.alpha * (
                reward + self.discount * self.get_value(next_state))
