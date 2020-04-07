from scipy.special import comb
import numpy as np
import matplotlib.pyplot as plt  # used
from rl_glue import RLGlue  # used
from tqdm import tqdm  # used
from rl_glue_pro import Pro
from report.report import make_figure

class Training:

    def __init__(self, environment, agent):

        self.env = environment
        self.agent = agent
        # number of actions
        closed = self.env.system.closed_switches
        opened = self.env.system.opened_switches
        num_closed = len(closed)
        num_opened = len(opened)
        num_actions = num_closed * num_opened
        # number of states
        start_tie = self.env.system.start_tie_obs
        switches_obs = self.env.system.switches_obs
        num_tie = len(start_tie)
        num_switches = len(switches_obs)
        self.num_states = int(comb(num_switches, num_tie))

        self.agent_info = {'num_actions': num_actions, 'num_states': self.num_states, 'epsilon': 0.1,
                      'discount': 1.0, 'step_size': 0.8}
        self.env_info = {}
        self.all_reward_sums = []
        self.all_state_visits = []

    def run_training(self, runs, episodes):

        num_runs = runs
        num_episodes = episodes

        for run in range(num_runs):
            self.agent_info['seed'] = run
            rl_glue = RLGlue(self.env, self.agent)
            rl_glue.rl_init(self.agent_info, self.env_info)

            reward_sums = []
            state_visits = np.zeros(self.num_states)
            for episode in tqdm(range(num_episodes)):
                if episode < num_episodes - 10:
                    rl_glue.rl_episode(0)
                else:
                    state, action = rl_glue.rl_start()
                    state_visits[state] += 1
                    is_terminal = False
                    while not is_terminal:
                        reward, state, action, is_terminal = rl_glue.rl_step()
                        state_visits[state] += 1

                reward_sums.append(rl_glue.rl_return())

            self.all_reward_sums.append(reward_sums)
            self.all_state_visits.append(state_visits)

            plt.plot(np.mean(self.all_reward_sums, axis=0), label='algorithm')
            plt.xlabel("Episodes")
            plt.ylabel("Sum of\n rewards\n during\n episode", rotation=0, labelpad=40)
            plt.legend()
            plt.grid
            plt.show()
            make_figure(None, np.mean(self.all_reward_sums, axis=0), 'training.html')



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

        # Failure is stated and actions are obtained
        failure_actions = self.env.get_failure_actions(failure)

        # number of states
        start_tie = self.env.system.start_tie_obs
        switches_obs = self.env.system.switches_obs
        num_tie = len(start_tie)
        num_switches = len(switches_obs)
        self.num_states = int(comb(num_switches, num_tie))

        self.agent_info = {'num_actions': num_actions, 'num_states': self.num_states, 'epsilon': 0.1,
                      'discount': 1.0, 'step_size': 0.8, 'q_values': q_values}

        self.agent.failure_actions = failure_actions

        self.env_info = {}
        self.all_reward_sums = []
        self.all_state_visits = []

    def run_production(self, runs, episodes):

        num_runs = runs
        num_episodes = episodes

        for run in range(num_runs):
            self.agent_info['seed'] = run
            rl_glue = Pro(self.env, self.agent)
            rl_glue.rl_init(self.agent_info, self.env_info)

            reward_sums = []
            state_visits = np.zeros(self.num_states)
            for episode in tqdm(range(num_episodes)):
                #self.env.system.system_data.open_dss.open_init()
                print(self.env.system.system_data.open_dss.get_voltage()[32])
                print('------------------------------')
                print('Episode: ', episode)
                if episode < num_episodes - 10:
                    rl_glue.rl_episode(0)
                else:
                    state, action = rl_glue.rl_start()
                    state_visits[state] += 1
                    is_terminal = False
                    while not is_terminal:
                        reward, state, action, is_terminal = rl_glue.rl_step()
                        state_visits[state] += 1

                reward_sums.append(rl_glue.rl_return())

            self.all_reward_sums.append(reward_sums)
            self.all_state_visits.append(state_visits)

            plt.figure(2)
            plt.plot(np.mean(self.all_reward_sums, axis=0), label='algorithm')
            plt.xlabel("Episodes")
            plt.ylabel("Sum of\n rewards\n during\n episode", rotation=0, labelpad=40)
            plt.legend()
            plt.grid
            plt.show()

            make_figure(None, np.mean(self.all_reward_sums, axis=0), "production.html")
