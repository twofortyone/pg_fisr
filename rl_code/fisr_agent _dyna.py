from rl_bases.agent import BaseAgent
import numpy as np


class QLearningAgent(BaseAgent):

    def __init__(self, mode):  # checked
        self.num_actions = None
        self.num_states = None
        self.epsilon = None
        self.step_size = None
        self.discount = None
        self.rand_generator = None
        self.prev_action = None
        self.prev_state = None
        self.failure_actions = None
        # Create an array for action-value estimates and initialize to zero
        self.q = None
        self.mode = mode  # 1 = training and 0 for production

    def agent_init(self, agent_init_info={}):

        self.num_actions = agent_init_info['num_actions']
        self.num_states = agent_init_info['num_states']
        self.epsilon = agent_init_info['epsilon']
        self.step_size = agent_init_info['step_size']
        self.discount = agent_init_info['discount']
        self.rand_generator = np.random.RandomState(agent_init_info['seed'])
        self.prev_action = None
        self.prev_state = None

        # Mode == 1 for training and 0 for production
        if self.mode == 1: self.q = np.zeros((self.num_states, self.num_actions))
        elif self.mode == 0: self.q = agent_init_info['q_values']


    def agent_start(self, state):
        # choose action using epsilon greedy
        current_q = self.q[state]
        if self.rand_generator.rand() < self.epsilon:
            action = self.rand_generator.randint(self.num_actions)
        else:
            action = self.argmax(current_q)
        self.prev_state = state
        self.prev_action = action
        return action

    def agent_step(self, reward, state):
        """A step taken by the agent 

        :param reward: (float) the reward received for the last action taken
        :param state: (int) the state from the environment's step based on where
            the agent ended up after the last step 
        :return action(int): the last action the agent is taking
        """
        current_q = self.q[state]
        if self.rand_generator.rand() < self.epsilon: 
            action = self.rand_generator.randint(self.num_actions)
        else: 
            action = self.argmax(current_q)

        # Perform an update 
        ps = self.prev_state
        pa = self.prev_action
        aux = reward + self.discount * np.amax(current_q) - self.q[ps, pa]
        self.q[ps, pa] = self.q[ps, pa] + self.step_size * aux

        self.prev_state = state
        self.prev_action = action
        return action 

    def agent_end(self, reward):
        """Run when the agent terminates
        :param reward: (float) the reward the agent received for
        entering the terminal state         
        """
        # perform the last update in the episode 
        ps = self.prev_state
        pa = self.prev_action
        qsa = self.q[ps, pa]
        self.q[ps, pa] = qsa + self.step_size*(reward-qsa)

    def agent_cleanup(self):
        self.prev_state = None 

    def agent_message(self, message):
        """A function used to pass information from the agent to the experiment.
        :param message: The message passed to the agent.
        :return: The response (or answer) to the message.
        """
        if message == "get_values":
            return self.q
        else:
            raise Exception("TDAgent.agent_message(): Message not understood!")

    def argmax(self, q_values):
        """ argmax with random tie-breaking 
        :param q_values: (numpy array) the array of action-values
        :return action (int): an action with the highest value
        """

        top = float('-inf')
        ties = []
        for i in range(len(q_values)):
            if q_values[i] > top:
                top = q_values[i]
                ties = []

            if q_values[i] == top:
                ties.append(i)

        return self.rand_generator.choice(ties)
