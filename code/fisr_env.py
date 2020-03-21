from environment import BaseEnvironment
from dissystem import DistributionSystem
from itertools import combinations
from scipy.special import comb
import numpy as np


class FisrEnvironment(BaseEnvironment):
    """Implements the environment  
    """
    
    def __init__(self):
        nodes = ['N0', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6']
        switches = ['S1', 'S2', 'S3', 'S6', 'T4', 'T5']
        switches_conn = [('N0','N1'), ('N1','N2'),('N1','N3'),('N2','N4'),('N3','N4'),('N4','N5')]
        tie = ['T4', 'T5']
        self.dsystem = DistributionSystem(nodes,switches,tie, switches_conn)
        
        self.current_state = [None, None, None, None]
        reward = None
        observation = None
        termination = None
        self.reward_obs_term = [reward, observation, termination]

    def env_init(self, env_info={}):
        """Setup forn the environment called when the experiment first starts
        
        :param: env_info: information about the environment
        """

        self.reward_obs_term = [0.0, None, False]

        # self.switches = env_info.get('num_switches')
        self.start_tie_switches = [33, 34, 35, 36, 37]

        return self.reward_obs_term[1]

    def env_start(self, state):
        raise NotImplementedError

    def get_observation(self):
        num_sw = len(self.dsystem.switches_obs)
        num_tie = len(self.dsystem.opened_switches)
        print(num_sw,num_tie)
        switches = np.arange(1, num_sw +1)
        states = list(combinations(switches,num_tie))
        print(switches,states)
        tie = tuple(self.dsystem.opened_switches)
        print(tie)
        return states.index(tie)

    def env_step(self, action):
        """A step taken by the environment

        :param action: the action taken by the agent
        :return self.reward_obs_term (float, state, boolean): a tuple 
            of the reward, state observation and boolean indicating if it's terminal        
        """
        reward = 0

        self.reward_obs_term (reward)

    def env_cleanup(self):
        """Cleanup done after the environment ends"""
        self.dsystem.sys_start()

    def env_message(self, message):
        """A message asking the environment for information

        :param message (string): the message passed to the environment
        :return string: the response (or answer) to the message
        """
        if message == "what is the current reward?":
            return "{}".format(self.reward_obs_term[0])

        # else
        return "I don't know how to respond to your message"
