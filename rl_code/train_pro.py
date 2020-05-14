from scipy.special import comb
import numpy as np
from rl_bases.rl_glue import RLGlue
from tqdm import tqdm, trange
from rl_bases.rl_glue_pro import Pro
from report.report import make_figure
import time


class Training:

    def __init__(self, environment, agent, report_folder):
        t0 = time.time()
        self.env = environment
        t1 = time.time()
        self.agent = agent
        t2 = time.time()
        #print(f'env init time: {t1-t0}; agent init time: {t2-t1}')
        self.rf = report_folder
        # number of actions
        num_actions = self.env.num_actions
        # number of states
        self.num_states = self.env.num_states

        self.agent_info = {'num_actions': num_actions, 'num_states': self.num_states,
                           'epsilon': 0.1, 'discount': 1.0, 'step_size': 0.1}
        self.env_info = {}
        self.all_reward_sums = []
        self.all_state_visits = []

    def run_training(self, runs, episodes):

        num_runs = runs
        num_episodes = episodes

        for run in range(num_runs):
            self.agent_info['seed'] = run
            tr5 = time.time()
            rl_glue = RLGlue(self.env, self.agent)
            rl_glue.rl_init(self.agent_info, self.env_info)
            tr6 = time.time()

            reward_sums = []

            state_visits = np.zeros(self.num_states)
            tr7= time.time()
            for episode in trange(num_episodes):
                if episode < num_episodes: # - 10:
                    num_failures = rl_glue.environment.opendss.num_lines
                    for i in range(num_failures):
                        rl_glue.environment.failure = i
                        rl_glue.environment.opendss.fail_line(i)
                        rl_glue.environment.opendss.solve()
                        rl_glue.rl_episode(0)
                        #print(f'falla{i}')
                        rl_glue.environment.opendss.failure_restoration(i)
                        rl_glue.environment.opendss.solve()

                else:
                    state, action = rl_glue.rl_start()
                    state_visits[state] += 1
                    is_terminal = False
                    while not is_terminal:
                        reward, state, action, is_terminal = rl_glue.rl_step()
                        state_visits[state] += 1

                reward_sums.append(rl_glue.rl_return())
            tr8 = time.time()
            #print(f'rlglue t: {tr5-tr5}; state_visits:{tr7-tr6}; episode time:{tr8-tr7}')
            self.all_reward_sums.append(reward_sums)
            self.all_state_visits.append(state_visits)
        return make_figure(None, np.mean(self.all_reward_sums, axis=0), self.rf + 'training.html')


class Production:

    def __init__(self, environment, agent, q_values, failure, report_folder):

        self.env = environment
        self.agent = agent
        self.failure = failure
        self.rf = report_folder
        # number of actions
        closed = self.env.system.closed_switches
        opened = self.env.system.opened_switches
        num_closed = len(closed)
        num_opened = len(opened)
        num_actions = num_closed * num_opened

        # Failure is stated and actions are obtained
        failure_actions = self.env.get_failure_actions(self.failure)
        post_facts = self.env.get_post_facts(self.failure)

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
                state, action = rl_glue.rl_start()
                state_visits[state] += 1
                is_terminal = False
                while not is_terminal:
                    rl_step_data = rl_glue.rl_step(self.failure)
                    reward, state, action, is_terminal = rl_step_data[0]
                    taken_actions.append(rl_step_data[1])
                    state_visits[state] += 1

                reward_sums.append(rl_glue.rl_return())

            self.all_reward_sums.append(reward_sums)
            self.all_state_visits.append(state_visits)

        return [make_figure(None, np.mean(self.all_reward_sums, axis=0), 'production.html'),
                taken_actions]
