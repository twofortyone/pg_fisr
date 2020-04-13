
from bases.environment import BaseEnvironment
from dissystem import DistributionSystem
from itertools import combinations
import numpy as np
import time


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

    # -----------------------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------------------

    def get_voltage_limits(self):
        """Number of nodes out of limits
        :return: number of nodes out of limits
        """
        voltages = np.copy(self.system.system_data.open_dss.get_voltage())
        v_aux = voltages[:, 0]
        v_aux1 = v_aux[np.where(v_aux < 0.9)]
        v_aux2 = v_aux[np.where(v_aux > 1.05)]
        return len(v_aux1) + len(v_aux2)

    def get_states(self):
        """States list depending on tie and total switches
        :return states: (np array) total switches combing tie switches list
        """
        nt = len(self.system.start_tie_obs)
        switches = np.arange(self.system.num_switches)
        states = tuple(combinations(switches, nt))
        return np.asarray(states)

    def get_actions(self):
        """Actions list depending on current state
        :returns actions: (np.array) action list to take
        """
        closed = np.sort(self.system.closed_switches)
        opened = np.sort(self.system.opened_switches)

        actions = np.zeros((len(closed) * len(opened), 2))
        for i in range(len(closed)):
            actions[i * len(opened):i * len(opened) + len(opened), 0] = closed[i]
            actions[i * len(opened):i * len(opened) + len(opened), 1] = opened

        actions = actions.astype(int)
        return actions

    def get_failure_actions(self, failure):
        actions = self.get_actions()
        aux = actions[:, 0]
        pos = np.where(aux == failure)
        return pos[0]
    
    def get_post_facts(self, failure):
        actions = self.get_actions()
        aux = actions[:, 1]
        pos = np.where(aux != failure)
        return pos[0]

    def get_observation(self):
        """ Get state index
        :return pos: (int) index of current_state in states list
        """
        current_state = tuple(np.sort(self.system.opened_switches))
        # print(current_state)
        # Todo delete printing
        a = self.states.copy()
        aux_list = []
        for i in range(self.states.shape[1]):  # forward
            aux = a[:, i]
            pos_vec = np.where(aux == current_state[i])
            a = a[pos_vec, :][0]
            aux_list.append(pos_vec[0])
        pos = 0
        for i in range(self.states.shape[1]):  # backward
            pos = aux_list[self.states.shape[1] - 1 - i][pos]
        
        # update possible actions
        self.actions = self.get_actions()
        return pos

    # -----------------------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------------------
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

        # print('action:', action)
        # print('switches: ', switches)

        self.system.open_switch(switch2open)
        self.system.close_switch(switch2close)
        self.system.system_solver()
        # print(self.system.system_data.open_dss.get_voltage()[32])
        
        self.current_state = self.get_observation()  # update current state

        if self.system.num_nodes_offline() != 0:  # reward if there is any node offline
            reward -= 100

        if self.get_voltage_limits() != 0:
            reward -= 100

        if self.time_step == 10000:  # terminate if 1000 time steps are reached
            is_terminal = True
            self.time_step = 0
            self.system.sys_start()
            self.system.system_data.open_dss.open_init()

        self.reward_obs_term = [reward, self.current_state, is_terminal]

        return self.reward_obs_term

    def env_step_pro(self, action):
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

        # print('action:', action)
        # print('switches: ', switches)

        self.system.open_switch(switch2open)
        self.system.close_switch(switch2close)
        self.system.system_solver()
        # print(self.system.system_data.open_dss.get_voltage()[32])
    
        self.current_state = self.get_observation()  # update current state
        
        if self.system.num_nodes_offline() != 0:  # reward if there is any node offline
            reward -= 100

        if self.get_voltage_limits() != 0:
            reward -= 100

        nodes = self.system.num_nodes_offline()

        if (nodes == 0) and self.get_voltage_limits() == 0:
            is_terminal = True
            self.system.sys_start()
            self.system.system_data.open_dss.open_init()
        elif self.time_step == 100:
            is_terminal = True
            self.time_step = 0
            self.system.sys_start()
            self.system.system_data.open_dss.open_init()
            print('')

        self.reward_obs_term = [reward, self.current_state, is_terminal]

        return [self.reward_obs_term, switches.tolist()]

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
