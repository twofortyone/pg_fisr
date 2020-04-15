from scipy.special import comb
import numpy as np
from rl_bases.rl_glue_pro import Pro
from report.report import make_figure
import pandas as pd
from rl_code.fisr_env import FisrEnvironment
from rl_code.fisr_agent import QLearningAgent

report_folder = "E:/MININT/SMSOSD/OSDLOGS/github/pg_fisr/code/report/"


class Production:

    def __init__(self, environment, agent, q_values, failure):

        self.env = environment
        self.agent = agent
        # number of actions
        closed = self.env.system.closed_switches
        opened = self.env.system.opened_switches
        num_closed = len(closed)
        num_opened = len(opened)
        num_actions = num_closed * num_opened
        self.failure = failure

        # Failure is stated and actions are obtained
        failure_actions = self.env.get_failure_actions(failure)
        post_facts = self.env.get_post_facts(failure)

        # number of states
        start_tie = self.env.system.start_tie_obs
        switches_obs = self.env.system.switches_obs
        num_tie = len(start_tie)
        num_switches = len(switches_obs)
        self.num_states = int(comb(num_switches, num_tie))

        self.agent_info = {'num_actions': num_actions, 'num_states': self.num_states, 'epsilon': 0.1,
                           'discount': 1.0, 'step_size': 0.8, 'q_values': q_values}

        self.agent.failure_actions = failure_actions
        self.agent.post_facts = post_facts

        self.env_info = {}
        self.all_reward_sums = []
        self.all_state_visits = []

    def run_production(self, runs, episodes):

        num_runs = runs
        num_episodes = episodes
        taken_actions = []

        for run in range(num_runs):
            self.agent_info['seed'] = run
            rl_glue = Pro(self.env, self.agent)
            rl_glue.rl_init(self.agent_info, self.env_info)

            reward_sums = []
            state_visits = np.zeros(self.num_states)
            for episode in range(num_episodes):
                if episode < num_episodes - 10:
                    rl_glue.rl_episode(0)
                else:
                    state, action = rl_glue.rl_start()
                    state_visits[state] += 1
                    is_terminal = False
                    while not is_terminal:
                        rl_step_data = rl_glue.rl_step(self.failure)
                        print('hola')
                        reward, state, action, is_terminal = rl_step_data[0]
                        taken_actions.append(rl_step_data[1])
                        state_visits[state] += 1

                reward_sums.append(rl_glue.rl_return())

            self.all_reward_sums.append(reward_sums)
            self.all_state_visits.append(state_visits)

        return [make_figure(None, np.mean(self.all_reward_sums, axis=0), report_folder + 'production.html'),
                taken_actions]


q = pd.read_feather('E:/q_2tie_1r_50e_2000ts.ftr')
q_values = q.to_numpy()

env = FisrEnvironment()
agent = QLearningAgent()

production = Production(env, agent, q_values, 0)
pro = production.run_production(1, 1)
