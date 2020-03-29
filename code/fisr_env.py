from environment import BaseEnvironment
from dissystem import DistributionSystem
from dissystem import ToPython
from itertools import combinations
import numpy as np


class FisrEnvironment(BaseEnvironment):
    """Implements the environment
    Note:
        env_init, env_start, env_step, env_cleanup, and env_message are required
        methods.
    """
    
    def __init__(self):

        self.system = DistributionSystem()  # Create a distribution system model
        self.states = self.get_states()  # States depending on number of total and tie switches
        reward = None
        observation = None
        termination = None
        self.time_step = 0
        self.current_state = None
        self.reward_obs_term = [reward, observation, termination]
        self.actions = None

    def env_init(self, env_info={}):
        self.reward_obs_term = [0.0, None, False]

    def env_start(self):
        """The first method called when the experiment starts, called before the
        agent starts
        :return: (list) the first observation from the environment
        """
        self.current_state = self.get_observation()
        self.reward_obs_term[1] = self.current_state
        return self.reward_obs_term[1]

    def get_states(self):
        """States list depending on tie and total switches
        :return states: (tuple) total switches combing tie switches list
        """
        nt = len(self.system.start_tie_obs)
        switches = np.arange(self.system.num_switches)
        states = tuple(combinations(switches, nt))
        return states

    def get_observation(self):
        """ Get state index
        :return pos: (int) index of current_state in states list
        """
        current_state = tuple(np.sort(self.system.opened_switches))
        pos = self.states.index(current_state)

        # update possible actions
        self.actions = self.get_actions()
        return pos

    def env_step(self, action):
        """A step taken by the environment
        :param action: (int) the action taken by the agent (action, switch)
        :return: (list) a list of the reward, state observation and boolean if it's terminal
        """

        self.time_step += 1
        reward = -1
        is_terminal = False
        # determine switches to execute
        switches = self.actions[action]
        switch2open = switches[0]
        switch2close = switches[1]

        self.system.open_switch(switch2open)
        self.system.close_switch(switch2close)

        self.current_state = self.get_observation()  # update current state

        if self.system.num_nodes_offline() != 0:  # reward if there is any node offline
            reward -= 100

        if self.time_step == 100:  # terminate if 1000 time steps are reached
            is_terminal = True
            self.time_step = 0

        self.reward_obs_term = [reward, self.current_state, is_terminal]

        return self.reward_obs_term

    def env_cleanup(self):
        """Cleanup done after the environment ends"""
        r = self.system.sys_start()
        self.reward_obs_term = [0.0, None, False]
        self.env_start()
        return r

    def env_message(self, message):
        """ A message asking the environment for information
        :param message: the message passed to the environment
        :return: the response to the message
        """
        if message == "what is the current reward?":
            return "{}".format(self.reward_obs_term[0])

        else:
            return "I don't know how to respond to your message"

    def get_actions(self):
        """Actions list depending on current state
        :returns actions: (np.array) action list to take        
        """
        closed = np.sort(self.system.closed_switches)
        opened = np.sort(self.system.opened_switches)
        num_actions = len(closed) * len(opened)
        actions = np.zeros((num_actions, 2))
        i = 0
        for x in closed:
            for z in opened:
                actions[i] = np.array([x, z])
                i += 1
        actions = actions.astype(int)
        return actions

    def get_failure_actions(self, failure):
        actions = self.get_actions()
        aux = actions[:, 0]
        pos = np.where(aux == failure)
        return pos[0]
