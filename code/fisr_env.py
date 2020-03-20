from environment import BaseEnvironment
import numpy as np


class FisrEnvironment(BaseEnvironment):

    def __init__(self):
        self.start_tie_switches = [33, 34, 35, 36]
        self.current_state = [None, None, None, None]
        reward = None
        observation = None
        termination = None

    def env_init(self, env_info={}):
        self.reward_obs_term = [0.0, None, False]

        # self.switches = env_info.get('num_switches')
        self.start_tie_switches = [33, 34, 35, 36, 37]

    def env_start(self, state):
        raise NotImplementedError

    def env_step(self, action):
        raise NotImplementedError

    def env_cleanup(self):
        raise NotImplementedError

    def env_message(self, message):
        raise NotImplementedError
