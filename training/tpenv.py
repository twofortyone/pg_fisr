from bases.environment import BaseEnvironment
from itertools import product
import numpy as np


class FisrEnvironment_Pro(BaseEnvironment):
    """Implements the environment
    Note:
        env_init, env_start, env_step, env_cleanup, and env_message are required
        methods.
    """
    def __init__(self,  OpenDSSCOM, voltages, iso_loads, nloops):
        self.opendss = OpenDSSCOM  # Create a distribution system model
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

        self.voltages = voltages
        self.isolated_loads = iso_loads
        self.terminal_states = None
        self.num_loops = nloops

    # -----------------------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------------------
    def get_states(self):
        num_switches = self.opendss.num_switches
        num_lines = self.opendss.num_lines
        num_states = (2**num_switches)*num_lines
        return np.arange(num_states)

    def get_num_voltage_violations(self, state):  # checked
        """Number of nodes out of limits
        :return: number of nodes out of limits
        """
        va = np.asarray(self.voltages[state])
        violations = va[(va > 0.1) & (va <= 0.95) | (va >= 1.05)]
        return violations.shape[0]

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
        return [self.failure * self.num_switch_states + switch_state_pos, (self.opendss.lines[self.failure], current_state)]

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
        obs = self.get_observation()  # Find and update self.current_state
        self.current_state = obs[0]
        print(self.current_state)
        # update possible actions
        self.actions = self.get_actions()
        self.reward_obs_term[1] = self.current_state
        print(self.current_state,'-------------------')
        return self.reward_obs_term[1]

    def env_step(self, switch):
        """A step taken by the environment
        :param action: (int) the action taken by the agent (action, switch)
        :return: (list) a list of the reward, state observation and boolean if it's terminal
        """
        self.time_step += 1
        reward = -1
        is_terminal = False
        action = None

        num_loads_offline_prev = self.isolated_loads[self.current_state]
        num_loads_offline = 0
        v_out_of_limits = 0

        if self.current_state == self.terminal_states[self.failure]:
            is_terminal = True
            reward += 1000
            self.time_step = 0
            self.opendss.com_init()
            num_loads_offline = self.isolated_loads[self.current_state]
        else:
            action = self.actions[switch]
            if action == 1:
                self.opendss.close_switch(switch)  # close switch
            elif action == 0:
                self.opendss.open_switch(switch)  # open switch

            self.current_state = self.get_observation()[0]  # update current state
            self.actions = self.get_actions()
            num_loads_offline = self.isolated_loads[self.current_state]
            v_out_of_limits = self.voltages[self.current_state]
            num_loops = self.num_loops[self.current_state]

            print(f'state:{self.current_state}; {self.opendss.get_switches_status()}; num_iso: {num_loads_offline}; num_vol: {v_out_of_limits}')
            if num_loads_offline !=0: reward -= 10 * int(num_loads_offline)
            if num_loops != 0: reward -= 100
            if v_out_of_limits != 0: reward -= 10

            if self.current_state == self.terminal_states[self.failure]:
                is_terminal = True
                reward += 1000
                self.time_step = 0
                self.opendss.com_init()

        self.reward_obs_term = [reward, self.current_state, is_terminal]
        return [self.reward_obs_term, (self.opendss.switches[switch],action), num_loads_offline_prev, num_loads_offline, v_out_of_limits]

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

