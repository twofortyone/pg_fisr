from rl_bases.environment import BaseEnvironment
from rl_code.production.tcp import OpenDSSG
from itertools import product
import numpy as np
import time


class FisrEnvironment(BaseEnvironment):
    """Implements the environment
    Note:
        env_init, env_start, env_step, env_cleanup, and env_message are required
        methods.
    """
    def __init__(self, ts_cond):
        self.opendss_g = OpenDSSG()  # Create a distribution system model
        self.states = self.get_states()  # States depending on number of total and tie switches
        self.switch_states_dict = self.get_switch_states_dict()  # todo revisar si mejor busqueda binaria
        self.num_switch_states = 2**self.opendss_g.num_switches
        self.num_states = self.num_switch_states*self.opendss_g.num_lines
        self.failure = None
        reward = None
        observation = None
        termination = None
        self.time_step = 0
        self.current_state = None
        self.reward_obs_term = [reward, observation, termination]
        self.actions = None
        self.num_actions = self.opendss_g.num_switches
        self.ts_cond = ts_cond

    # -----------------------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------------------
    def get_states(self):
        num_switches = self.opendss_g.num_switches
        num_lines = self.opendss_g.num_lines
        num_states = (2**num_switches)*num_lines
        return np.arange(num_states)

    def get_voltage_limits(self):  # checked
        """Number of nodes out of limits
        :return: number of nodes out of limits
        """
        v_aux = self.opendss_g.get_voltage_magpu()
        v_aux1 = v_aux[np.where(v_aux < 0.9)]
        v_aux2 = v_aux[np.where(v_aux > 1.05)]
        return len(v_aux1) + len(v_aux2)

    def get_switch_states_dict(self): 
        """States list depending on tie and total switches
        :return states: (np array) total switches combing tie switches list
        """
        num_switches = self.opendss_g.num_switches
        switch_state = [0, 1]
        switch_states = list(product(switch_state, repeat=num_switches))
        ss_list = [str(x).strip('()').replace(',', '').replace(' ', '') for x in switch_states]
        ss_dict = dict(zip(ss_list, range(len(ss_list))))
        return ss_dict

    def get_actions(self):  # checked
        """Actions list depending on current state
        :returns actions: (np.array) action list to take
        """
        current_state = np.asarray(self.opendss_g.get_switches_status())
        return np.where(current_state == 1, 0, 1)

    def get_observation(self):  # checked
        """ Get state index
        :return pos: (int) index of current_state in states list
        """
        current_state = self.opendss_g.get_switches_status()
        cs = str(current_state).strip('[]').replace(',', '').replace(' ', '')

        switch_state_pos = self.switch_states_dict[cs]
        return self.failure * self.num_switch_states + switch_state_pos

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
        print(f'estado inicial:{self.current_state}: {self.opendss_g.get_switches_status()}')
        print(f'voltages out of limits:{self.get_voltage_limits()}')
        #print(self.current_state,'-------------------')

        return self.reward_obs_term[1]

    def env_step(self, switch):
        """A step taken by the environment
        :param action: (int) the action taken by the agent (action, switch)
        :return: (list) a list of the reward, state observation and boolean if it's terminal
        """

        self.time_step += 1
        reward = -1
        is_terminal = False
        # determine action to execute
        action = self.actions[switch]
        print(f'switch: {switch}; action:{action}')
        if action == 1: self.opendss_g.write_switch_status(switch, 1)
        elif action == 0: self.opendss_g.write_switch_status(switch, 0)

        self.current_state = self.get_observation()  # update current state
        self.actions = self.get_actions()
        num_loads_offline = None
        num_loops = None
        voltages_out_of_limit = self.get_voltage_limits()
        print(f'state:{self.current_state}; {self.opendss_g.get_switches_status()};voltages: {voltages_out_of_limit}')
        #if num_loads_offline !=0: reward -= 100 * num_loads_offline
        #if num_loops != 0: reward -= 100
        if voltages_out_of_limit != 0: reward -= 10 * voltages_out_of_limit      

        # Todo rest: if offline == 1 and loop == 0 and self.get_voltage_limits() == 0:
        #if self.get_voltage_limits() == 0:
        #    is_terminal = True
        #    self.opendss_g.openddsg_init()
        #elif self.time_step == 100:
        if self.time_step == 1:
            is_terminal = True
            self.time_step = 0
            print(f' cs: {self.current_state}')
            print(self.opendss_g.get_switches_status())
            self.opendss_g.openddsg_init()
        self.reward_obs_term = [reward, self.current_state, is_terminal]

        return [self.reward_obs_term, [f'S:{switch}', f'A:{action}']]

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

