from environment import BaseEnvironment
from dissystem import DistributionSystem
from dissystem import ToPython
from itertools import combinations
import numpy as np


class FisrEnvironment(BaseEnvironment):
    """Implements the environment  
    """
    
    def __init__(self):

        nodes = ['N0', 'N1', 'N2', 'N3', 'N4', 'N5']  # Node list
        conn = [('N0', 'N1'), ('N1', 'N2'), ('N1', 'N3'), ('N4', 'N5'), ('N2', 'N4'), ('N3', 'N4')]
        switches = ['S1', 'S2', 'S3', 'S6', 'T4', 'T5']  # Switch list
        tie = ['T4', 'T5']  # Tie switch list
        self.system_data = ToPython(nodes, switches, tie, conn)  # Convert system data to python system
        self.system = DistributionSystem(self.system_data)  # Create a distribution system model

        self.states = self.get_states()  # States depending on number of total and tie switches
        reward = None
        observation = None
        termination = None
        self.reward_obs_term = [reward, observation, termination]
        # Until here
        self.current_state = [None, None, None, None]

    def env_init(self, env_info={}):
        self.reward_obs_term = [0.0, None, False]
        return NotImplementedError

    def env_start(self):
        raise NotImplementedError

    def get_states(self):
        ns = len(self.system.switches_obs)
        nt = len(self.system.start_tie_obs)
        switches = np.arange(1, ns+1)
        states = tuple(combinations((switches, nt)))
        return states

    def get_observation(self):
        current_state = self.system.sort_opened_switches()
        pos = self.states.index(current_state)
        return pos

    def env_step(self, action):
        return NotImplementedError

    def env_cleanup(self):
        return NotImplementedError

    def env_message(self, message):
        if message == "what is the current reward?":
            return "{}".format(self.reward_obs_term[0])

        # else
        return "I don't know how to respond to your message"



