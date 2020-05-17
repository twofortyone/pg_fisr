from rl_bases.environment import BaseEnvironment
from rl_code.training.com import OpenDSSCOM
import pandas as pd
from itertools import product
import numpy as np
import time


class FisrEnvironment(BaseEnvironment):
    """Implements the environment
    Note:
        env_init, env_start, env_step, env_cleanup, and env_message are required
        methods.
    """
    def __init__(self, path, ts_cond, v_ftr):
        self.opendss = OpenDSSCOM(path)  # Create a distribution system model
        self.states = self.get_states()  # States depending on number of total and tie switches
        self.switch_states_dict = self.get_switch_states_dict() # todo revisar si mejor busqueda binaria
        self.num_switch_states = 2**self.opendss.num_switches
        self.num_states = self.num_switch_states*self.opendss.num_lines
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
        self.v_vtr = v_ftr
        if v_ftr== 1:
            self.voltages = np.asarray(pd.read_feather('E:/123bus_voltages.ftr'))
    # -----------------------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------------------
    def get_states(self):
        num_switches = self.opendss.num_switches
        num_lines = self.opendss.num_lines 
        num_states = (2**num_switches)*num_lines
        return np.arange(num_states)

    def get_voltage_limits(self, state):  # checked
        """Number of nodes out of limits
        :return: number of nodes out of limits
        """
        v_aux = None
        if self.v_vtr ==1:
            v_aux = self.voltages[:, state]
        else:
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

    def env_start(self):  # checked
        """The first method called when the experiment starts, called before the
        agent starts
        :return: (list) the first observation from the environment
        """
        # Start system data (past in env_step::endcondition)
        #self.opendss.com_init()
        self.current_state = self.get_observation()  # Find and update self.current_state
        # update possible actions
        self.actions = self.get_actions()
        self.reward_obs_term[1] = self.current_state
        #print(self.current_state,'-------------------')

        return self.reward_obs_term[1]

    def env_step(self, switch):
        """A step taken by the environment
        :param action: (int) the action taken by the agent (action, switch)
        :return: (list) a list of the reward, state observation and boolean if it's terminal
        """
        self.time_step += 1
        #reward = -1
        reward = 0
        is_terminal = False
        action = self.actions[switch]
        # open/close switches
        te0 = time.time()
        if action==1: self.opendss.close_switch(switch)
        elif action==0: self.opendss.open_switch(switch)
        self.opendss.solve()
        #if self.v_vtr ==0: self.opendss.solve()
        #te1 = time.time()
        # get obs
        self.current_state = self.get_observation()  # update current state
        te2 = time.time()
        #print(self.opendss.get_voltage_magpu())
        # update possible actions
        self.actions = self.get_actions()
        #print(self.current_state, switch, action, self.actions)
        te3 = time.time()
        # restrictions
        num_loads_offline = self.opendss.get_num_isolated_loads()
        num_loops = self.opendss.get_num_loops()
        voltages_out_of_limit = self.get_voltage_limits(self.current_state)
        # nods = self.system.system_data.get_switches_names(self.states[self.current_state].tolist())
        # print(self.current_state, offline, loop, nods)

        if num_loads_offline !=0: reward -= 100 * num_loads_offline
        if num_loops != 0: reward -= 100
        if voltages_out_of_limit != 0: reward -= 100
        te4 = time.time()
        #print(f'ga:{te3-te2}; cs: {te2-te1}; os: {te1-te0}; total:{te3-te0}')
        # end condition
        if self.time_step == self.ts_cond:
            is_terminal = True
            self.time_step = 0
            self.opendss.com_init()
        self.reward_obs_term = [reward, self.current_state, is_terminal]
        return self.reward_obs_term

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


env = FisrEnvironment(('E:/pg_fisr/models/IEEE_123_FLISR_Case/Master.dss'), 1, 1)