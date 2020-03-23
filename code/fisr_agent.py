from agent import BaseAgent


class TDAgent(BaseAgent):
    def agent_init(self, agent_info={}):
        raise NotImplementedError

    def agent_start(self, state):
        raise NotImplementedError

    def agent_step(self, reward, state):
        raise NotImplementedError

    def agent_end(self, reward):
        raise NotImplementedError

    def agent_cleanup(self):
        raise NotImplementedError

    def agent_message(self, message):
        raise NotImplementedError