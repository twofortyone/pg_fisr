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
        
        # choose action using epsilon greedy
        curren_q = self.q[state,:]  # array with all q values for a given state
        if self.rand_generator.rand() < self.epsilon: 
            action = self.rand_generator.randint(self.num_actions)
        else: 
            action = self.argmax(curren_q)    
        self.prev_state = state
        self.prev_action = action
        return action  

    def agent_step(self, reward, state):
        """A step taken by the agent 
        :param reward(float): the reward received for the last action taken 
            state(int): the state from the environment's step based on where
            the agent ended up after the last step 
        :return action(int): the last action the agent is taking 
        """
        
        current_q = self.q[state]
        if self.rand_generator.rand() < self.epsilon: 
            action = self.rand_generator.randint(self.num_actions)
        else: 
            action = self.argmax(current_q)

        # Perform an update 
        qsa = self.q[self.prev_state, self.prev_action]
        aux = reward + self.discount * np.amax(current_q) - qsa
        self.q[self.prev_state, self.prev_action] = qsa + self.step_size * aux

        self.prev_state = state
        self.prev_action = action
        return action 

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