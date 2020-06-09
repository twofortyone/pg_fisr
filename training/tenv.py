from bases.environment import BaseEnvironment
from training.com import OpenDSSCOM
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
    def __init__(self, OpenDSSCOM, voltages, iso_loads, nloops):
        self.opendss = OpenDSSCOM  # Create a distribution system model
        self.states = self.get_states()  # States depending on number of total and tie switches
        self.switch_states_dict = self.get_switch_states_dict() # todo revisar si mejor busqueda binaria
        self.switch_states = self.get_switch_states_array()
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
        self.terminal_states= None
        self.num_loops = nloops
    # -----------------------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------------------
    def get_default_state(self):
        status = str(self.opendss.start_status).strip('[]').replace(' ', '')
        return self.switch_states_dict[status]

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
        switch_state = [0, 1]
        switch_states = list(product(switch_state, repeat=self.opendss.num_switches))
        ss_list = [str(x).strip('()').replace(',', '').replace(' ', '') for x in switch_states]
        ss_dict = dict(zip(ss_list, range(len(ss_list))))
        return ss_dict

    def get_switch_states_array(self):
        switch_state = [0, 1]
        return np.asarray(list(product(switch_state, repeat=self.opendss.num_switches)))

    def get_ss_from_state(self, state):
        return self.switch_states[self.get_ss_pos(state)]

    def get_ss_pos(self, state):
        return state - self.failure * self.num_switch_states


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
        reward = -10
        is_terminal = False
        action = None
        if self.current_state == self.terminal_states[self.failure]:
            is_terminal = True
            reward += 1000
            self.time_step = 0
            self.opendss.com_init()
        else:
            action = self.actions[switch]
            # switching operations
            if action==1: self.opendss.close_switch(switch)
            elif action==0: self.opendss.open_switch(switch)
            # get obs
            self.current_state = self.get_observation()  # update current state
            self.actions = self.get_actions() # update possible actions
            # restrictions
            num_loads_offline = self.isolated_loads[self.current_state]
            voltages_out_of_limit = self.voltages[self.current_state]
            # nods = self.system.system_data.get_switches_names(self.states[self.current_state].tolist())
            # print(self.current_state, offline, loop, nods)
            num_loops = self.num_loops[self.current_state]
            if num_loads_offline !=0: reward -= 10 * int(num_loads_offline)
            if num_loops != 0: reward -= 100
            if voltages_out_of_limit != 0: reward -= 10
            te4 = time.time()
            #print(f'ga:{te3-te2}; cs: {te2-te1}; os: {te1-te0}; total:{te3-te0}')
            # end condition
            if self.current_state == self.terminal_states[self.failure]:
            #if self.time_step ==1000:
                is_terminal = True
                reward += 1000
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

    def save_system_data(self,path):
        labels = ['circuit_name','num_lines', 'num_switches', 'num_loads', 'num_states', 'num_actions', 'num_qvalues']
        name = self.opendss.DSSCircuit.Name
        nl = self.opendss.num_lines
        nsw = self.opendss.num_switches
        nlo = self.opendss.num_loads
        ns = self.num_states
        na = self.num_actions
        nq = ns * na
        data = [name, nl, nsw, nlo, ns, na, nq]
        df = pd.DataFrame(data=data, columns=['data'], index= labels)
        df.to_excel(path)
        return [data, labels]


#com = OpenDSSCOM('E:/pg_fisr/data/models/IEEE_123_FLISR_Case/Master.DSS')
#env = FisrEnvironment(com, [], [], [])
