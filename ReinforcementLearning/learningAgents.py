import util


class ValueEstimationAgent:
    """
      Abstract agent which assigns values to (state,action)
      Q-Values for an environment. As well as a value to a
      state and a policy given respectively by,

      V(s) = max_{a in actions} Q(s,a)
      policy(s) = arg_max_{a in actions} Q(s,a)

      Both ValueIterationAgent and QLearningAgent inherit
      from this agent. While a ValueIterationAgent has
      a model of the environment via a MarkovDecisionProcess
      (see mdp.py) that is used to estimate Q-Values before
      ever actually acting, the QLearningAgent estimates
      Q-Values while acting in the environment.
    """

    def __init__(self, alpha=1.0, epsilon=0.05, gamma=0.8, num_training=10):
        """
        Sets options, which can be passed in via the Pacman command line using -a alpha=0.5,...
        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.discount = float(gamma)
        self.num_training = int(num_training)

    ####################################
    #    Override These Functions      #
    ####################################
    def get_qvalue(self, state, action):
        """
        Should return Q(state,action)
        """
        util.raise_not_defined()

    def get_value(self, state):
        """
        What is the value of this state under the best action?
        Concretely, this is given by

        V(s) = max_{a in actions} Q(s,a)
        """
        util.raise_not_defined()

    def get_policy(self, state):
        """
        What is the best action to take in the state. Note that because
        we might want to explore, this might not coincide with getAction
        Concretely, this is given by

        policy(s) = arg_max_{a in actions} Q(s,a)

        If many actions achieve the maximal Q-value,
        it doesn't matter which is selected.
        """
        util.raise_not_defined()

    def get_action(self, state):
        """
        state: can call state.getLegalActions()
        Choose an action and return it.
        """
        util.raise_not_defined()


class ReinforcementAgent(ValueEstimationAgent):
    """
      Abstract Reinforcement Agent: A ValueEstimationAgent
        which estimates Q-Values (as well as policies) from experience
        rather than a model

        What you need to know:
            - The environment will call
              observeTransition(state,action,nextState,deltaReward),
              which will call update(state, action, nextState, deltaReward)
              which you should override.
        - Use self.getLegalActions(state) to know which actions
              are available in a state
    """

    ####################################
    #    Override These Functions      #
    ####################################

    def update(self, state, action, next_state, reward):
        """
            This class will call this function, which you write, after
            observing a transition and reward
        """
        util.raise_not_defined()

    ####################################
    #    Read These Functions          #
    ####################################

    def get_legal_actions(self, state):
        """
          Get the actions available for a given
          state. This is what you should use to
          obtain legal actions for a state
        """
        return self.action_fn(state)

    def observe_transition(self, state, action, next_state, delta_reward):
        """
            Called by environment to inform agent that a transition has
            been observed. This will result in a call to self.update
            on the same arguments

            NOTE: Do *not* override or call this function
        """
        self.episode_rewards += delta_reward
        self.update(state, action, next_state, delta_reward)

    def start_episode(self):
        """
          Called by environment when new episode is starting
        """
        self.last_state = None
        self.last_action = None
        self.episode_rewards = 0.0

    def stop_episode(self):
        """
          Called by environment when episode is done
        """
        if self.episodes_so_far < self.num_training:
            self.accum_train_rewards += self.episode_rewards
        else:
            self.accum_test_rewards += self.episode_rewards
        self.episodes_so_far += 1
        if self.episodes_so_far >= self.num_training:
            # Take off the training wheels
            self.epsilon = 0.0  # no exploration
            self.alpha = 0.0  # no learning

    def is_in_training(self):
        return self.episodes_so_far < self.num_training

    def is_in_testing(self):
        return not self.is_in_training()

    def __init__(self, action_fn=None, num_training=100, epsilon=0.5, alpha=0.5, gamma=1):
        """
        actionFn: Function which takes a state and returns the list of legal actions

        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        self.episodes_so_far = None
        if action_fn is None:
            action_fn = lambda state: state.getLegalActions()
        self.actionFn = action_fn
        self.episodesSoFar = 0
        self.accum_train_rewards = 0.0
        self.accum_test_rewards = 0.0
        self.numTraining = int(num_training)
        self.epsilon = float(epsilon)
        self.alpha = float(alpha)
        self.discount = float(gamma)

    # ################################
    # # Controls needed for Crawler  #
    # ################################
    # def set_epsilon(self, epsilon):
    #     self.epsilon = epsilon
    #
    # def set_learning_rate(self, alpha):
    #     self.alpha = alpha
    #
    # def set_discount(self, discount):
    #     self.discount = discount
    #
    # def doAction(self, state, action):
    #     """
    #         Called by inherited class when
    #         an action is taken in a state
    #     """
    #     self.lastState = state
    #     self.lastAction = action
    #
    # ###################
    # # Pacman Specific #
    # ###################
    # def observationFunction(self, state):
    #     """
    #         This is where we ended up after our last action.
    #         The simulation should somehow ensure this is called
    #     """
    #     if not self.lastState is None:
    #         reward = state.getScore() - self.lastState.getScore()
    #         self.observeTransition(self.lastState, self.lastAction, state, reward)
    #     return state
    #
    # def registerInitialState(self, state):
    #     self.startEpisode()
    #     if self.episodesSoFar == 0:
    #         print('Beginning %d episodes of Training' % (self.numTraining))
    #
    # def final(self, state):
    #     """
    #       Called by Pacman game at the terminal state
    #     """
    #     delta_reward = state.getScore() - self.lastState.getScore()
    #     self.observeTransition(self.lastState, self.lastAction, state, delta_reward)
    #     self.stopEpisode()
    #
    #     # Make sure we have this var
    #     if 'episodeStartTime' not in self.__dict__:
    #         self.episodeStartTime = time.time()
    #     if 'lastWindowAccumRewards' not in self.__dict__:
    #         self.lastWindowAccumRewards = 0.0
    #     self.lastWindowAccumRewards += state.getScore()
    #
    #     NUM_EPS_UPDATE = 100
    #     if self.episodesSoFar % NUM_EPS_UPDATE == 0:
    #         print('Reinforcement Learning Status:')
    #         windowAvg = self.lastWindowAccumRewards / float(NUM_EPS_UPDATE)
    #         if self.episodesSoFar <= self.numTraining:
    #             trainAvg = self.accumTrainRewards / float(self.episodesSoFar)
    #             print('\tCompleted %d out of %d training episodes' % (self.episodesSoFar, self.numTraining))
    #             print('\tAverage Rewards over all training: %.2f' % (trainAvg))
    #         else:
    #             testAvg = float(self.accumTestRewards) / (self.episodesSoFar - self.numTraining)
    #             print('\tCompleted %d test episodes' % (self.episodesSoFar - self.numTraining))
    #             print('\tAverage Rewards over testing: %.2f' % testAvg)
    #         print('\tAverage Rewards for last %d episodes: %.2f' % (NUM_EPS_UPDATE, windowAvg))
    #         print('\tEpisode took %.2f seconds' % (time.time() - self.episodeStartTime))
    #         self.lastWindowAccumRewards = 0.0
    #         self.episodeStartTime = time.time()
    #
    #     if self.episodesSoFar == self.numTraining:
    #         msg = 'Training Done (turning off epsilon and alpha)'
    #         print('%s\n%s' % (msg, '-' * len(msg)))
