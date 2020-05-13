from rl_bases.environment import BaseEnvironment
from rl_code.opendss import OpenDSSCOM
from itertools import combinations, product
import numpy as np
from tqdm import tqdm
import time
import pandas as pd


class FisrEnvironment(BaseEnvironment):
    """Implements the environment
    Note:
        env_init, env_start, env_step, env_cleanup, and env_message are required
        methods.
    """
    def __init__(self, ts_cond):
        self.opendss = OpenDSSCOM('E:/IEEE_123_FLISR_Case/Master.dss')  # Create a distribution system model
        self.states = self.get_states()  # States depending on number of total and tie switches
        self.switch_states_dict = self.get_switch_states_dict() # todo revisar si mejor busqueda binaria
        self.failures_dict = self.get_failures_dict()
        self.num_switch_states = 2**self.opendss.num_switches
        self.num_states = self.num_switch_states*self.opendss.num_lines
        self.rand_generator = np.random.RandomState(412)
        self.failure = None
        reward = None
        observation = None
        termination = None
        self.time_step = 0
        self.current_state = None
        self.reward_obs_term = [reward, observation, termination]
        self.actions = None
        self.num_actions = self.opendss.num_switches
        self.ts_cond = ts_cond

    # -----------------------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------------------
    def get_states(self):
        num_switches = self.opendss.num_switches
        num_lines = self.opendss.num_lines 
        num_states = (2**num_switches)*num_lines
        return np.arange(num_states)

    def get_voltage_limits(self):  # checked
        """Number of nodes out of limits
        :return: number of nodes out of limits
        """
        v_aux = self.opendss.get_voltage_magpu()
        v_aux1 = v_aux[np.where(v_aux < 0.9)]
        v_aux2 = v_aux[np.where(v_aux > 1.05)]
        return len(v_aux1) + len(v_aux2)

    def get_switch_states_dict(self): 
        """States list depending on tie and total switches
        :return states: (np array) total switches combing tie switches list
        """
        num_switches = self.opendss.num_switches
        switch_state = [0, 1]
        switch_states = list(product(switch_state, repeat=num_switches))
        ss_list = [str(x).strip('()').replace(',', '').replace(' ', '') for x in switch_states]
        ss_dict = dict(zip(ss_list, range(len(ss_list))))
        return ss_dict

    def get_failures_dict(self):
        lines = self.opendss.lines
        return dict(zip(lines, range(self.opendss.num_lines)))

    def get_actions(self):  # checked
        """Actions list depending on current state
        :returns actions: (np.array) action list to take
        """
        current_state = np.asarray(self.opendss.get_switches_status())
        return np.where(current_state == 1, 0, 1)

    def get_observation(self):  # checked
        """ Get state index
        :return pos: (int) index of current_state in states list
        """
        current_state = self.opendss.get_switches_status()
        cs = str(current_state).strip('[]').replace(',', '').replace(' ', '')

        switch_state_pos = self.switch_states_dict[cs]
        return self.failure* self.num_switch_states + switch_state_pos

    # -----------------------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------------------
    def env_init(self, env_info={}):
        self.reward_obs_term = [0.0, None, False]
        self.failure = self.rand_generator.randint(self.opendss.num_lines)
        self.opendss.fail_line(self.failure)

    def env_start(self):  # checked
        """The first method called when the experiment starts, called before the
        agent starts
        :return: (list) the first observation from the environment
        """
        # Start system data (past in env_step::endcondition)
        #self.system.sys_start()
        self.current_state = self.get_observation()  # Find and update self.current_state
        # update possible actions
        self.actions = self.get_actions()
        self.reward_obs_term[1] = self.current_state
        # print(self.current_state,'-------------------')
        # offline = self.system.nodes_isolated()
        # loop = self.system.nodes_loop()
        # print(self.current_state, offline, loop)
        return self.reward_obs_term[1]

    def env_step(self, switch):
        """A step taken by the environment
        :param action: (int) the action taken by the agent (action, switch)
        :return: (list) a list of the reward, state observation and boolean if it's terminal
        """
        self.time_step += 1
        reward = -1
        # reward = 0
        is_terminal = False
        # determine switches to execute
        action = self.actions[switch]
        # open/close switches
        te0 = time.time()
        if action==1: self.opendss.close_switch(switch)
        elif action==0: self.opendss.open_switch(switch)
        self.opendss.solve()
        te1 = time.time()
        # get obs
        self.current_state = self.get_observation()  # update current state
        te2 = time.time()
        #print(self.system.get_voltage())
        # update possible actions
        self.actions = self.get_actions()
        #print(self.actions)
        te3 = time.time()
        # restrictions
        num_loads_offline = self.opendss.get_num_isolated_loads()
        num_loops = self.opendss.get_num_loops()
        voltages_out_of_limit = self.get_voltage_limits()
        # nods = self.system.system_data.get_switches_names(self.states[self.current_state].tolist())
        # print(self.current_state, offline, loop, nods)

        if num_loads_offline !=0: reward -= 100 * num_loads_offline
        if num_loops != 0: reward -= 100
        if voltages_out_of_limit != 0: reward -= 10 * voltages_out_of_limit
        te4 = time.time()
        #print(f'ga:{te3-te2}; cs: {te2-te1}; os: {te1-te0}; total:{te3-te0}')      

        # end condition
        if self.time_step == self.ts_cond:
            is_terminal = True
            self.time_step = 0
            self.opendss.failure_restoration(self.failure)

        # if offline == 1 and loop == 0 and self.get_voltage_limits() == 0:
        #    is_terminal = True
        # if self.get_voltage_limits() == 0:
        #    is_terminal = True
        #    self.time_step = 0
        #    reward +=1
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

        self.opendss.open_switch(switch2open)
        self.opendss.close_switch(switch2close)

        self.current_state = self.get_observation()  # update current state

        num_loads_offline = self.opendss.get_num_isolated_loads()
        num_loops = self.opendss.get_num_loops()
        voltages_out_of_limit = self.get_voltage_limits()

        if num_loads_offline !=0: reward -= 100 * num_loads_offline
        if num_loops != 0: reward -= 100
        if voltages_out_of_limit != 0: reward -= 10 * voltages_out_of_limit      

        # Todo rest: if offline == 1 and loop == 0 and self.get_voltage_limits() == 0:
        if offline == 1 and self.get_voltage_limits() == 0:
            is_terminal = True
            self.opendss.com_init()
        elif self.time_step == 100:
            is_terminal = True
            self.time_step = 0
            self.opendss.com_init()
        self.reward_obs_term = [reward, self.current_state, is_terminal]

        return [self.reward_obs_term, switches.tolist()]

    def env_cleanup(self):  # checked
        """Cleanup done after the environment ends"""
        self.reward_obs_term = [0.0, None, False]
        self.env_start()

    def env_message(self, message):  # checked
        """ A message asking the environment for information
        :param message: the message passed to the environment
        :return: the response to the message
        """
        if message == "what is the current reward?":
            return "{}".format(self.reward_obs_term[0])

        else:
            return "I don't know how to respond to your message"

