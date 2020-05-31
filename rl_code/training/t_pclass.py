import numpy as np
from tqdm import trange
from rl_bases.production.rl_glue_pro import Pro
from report.report import make_figure
import time


class Production:

    def __init__(self, environment, agent, q_values, failure, report_folder):

        self.env = environment
        self.agent = agent
        self.failure = failure
        self.rf = report_folder
        # number of actions
        num_actions = self.env.num_actions
        # number of states
        self.num_states = self.env.num_states

        self.agent_info = {'num_actions': num_actions, 'num_states': self.num_states, 'epsilon': 0.1,
                           'discount': 0.1, 'step_size': 0.8, 'q_values': q_values}

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
                # fail line
                rl_glue.environment.failure = self.failure
                rl_glue.environment.opendss.fail_line(self.failure)
                # rl start
                state, action = rl_glue.rl_start()
                state_visits[state] += 1
                is_terminal = False
                while not is_terminal:
                    # rl step
                    rl_step_data = rl_glue.rl_step()
                    reward, state, action, is_terminal = rl_step_data[0]
                    # record actions data
                    taken_actions.append(rl_step_data[1])
                    state_visits[state] += 1

                rl_glue.environment.opendss.failure_restoration(self.failure) # todo revisar si se debe restaurar
                reward_sums.append(rl_glue.rl_return())

            self.all_reward_sums.append(reward_sums)
            self.all_state_visits.append(state_visits)

        return [make_figure(None, np.mean(self.all_reward_sums, axis=0), 'production.html'),
                taken_actions]
