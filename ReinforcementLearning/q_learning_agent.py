import random


class QLearningAgent:
    def __init__(self, alpha, epsilon, discount, actions):
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.discount = float(discount)
        self.actions = actions
        self.q_values = {}

    def get_qvalue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we never seen
          a state or (state,action) tuple
        """
        if (state, action) not in self.q_values:
            return 0.0
        return self.q_values[(state, action)]

    def get_value(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        action_vals = [self.get_qvalue(state, action) for action in range(self.actions)]
        random.shuffle(action_vals)
        return max(action_vals)

    def get_policy(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        action_vals = [(action, self.get_qvalue(state, action)) for action in range(self.actions)]
        max_val = max([self.get_qvalue(state, action) for action in range(self.actions)])
        best_actions = [action for action, val in action_vals if val == max_val]
        return random.choice(best_actions)

    def get_action(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        r = random.random()

        if r < self.epsilon:
            return random.randint(0, self.actions - 1)

        return self.get_policy(state)

    def update(self, state, action, next_state, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here
          NOTE: You should never call this function,
          it will be called on your behalf
        """
        curr_q_val = self.get_qvalue(state, action)
        self.q_values[(state, action)] = (1 - self.alpha) * curr_q_val + self.alpha * (
                reward + self.discount * self.get_value(next_state))
