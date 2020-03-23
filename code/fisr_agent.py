from agent import BaseAgent
import numpy as np


class QLearningAgent(BaseAgent):

    def __init__(self, agent_init_info={}):

        self.num_actions = agent_init_info['num_actions']
        self.num_states = agent_init_info['num_states']
        self.epsilon = agent_init_info['epsilon']
        self.step_size = agent_init_info['step_size']
        self.discount = agent_init_info['discount']
        self.rand_generator = np.random.RandomState(agent_init_info['seed'])

        # Create an array for action-value estimates and initialize to zero
        self.q = np.zeros((self.num_states, self.num_actions))

    def agent_start(self, state):
        raise NotImplementedError        

    def agent_step(self, reward, state):
        raise NotImplementedError

    def agent_end(self, reward):
        raise NotImplementedError

    def agent_cleanup(self):
        raise NotImplementedError

    def agent_message(self, message):
        raise NotImplementedError

    def argmax(self, q_values):
        """ argmax with random tie-breaking 
        :param q_values (numpy arrary): the array of action-values
        :return action (int): an action with the highest value 
        """

        top = float('-inf')
        ties = []
        for i in range(len(q_values)):
            if q_values[i] < top: 
                top = q_values[i]
                ties = []

            if q_values == top:
                ties.append(i)

        return self.rand_generator.choice(ties)