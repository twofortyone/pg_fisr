import numpy as np
from rl_bases.rl_glue import RLGlue
from report.report import make_figure
import time
from tqdm import trange
import  pandas as pd

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
                    for i in range(1, num_failures):
                        rl_glue.environment.failure = i
                        rl_glue.environment.opendss.fail_line(i)
                        rl_glue.rl_episode(0)
                        #print(f'falla{i}')
                        rl_glue.environment.opendss.failure_restoration(i)

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
            df = pd.DataFrame(np.mean(self.all_reward_sums, axis=0), columns=['r_sums'])
            df.to_excel(f'{self.rf}ars.xlsx')
        return make_figure(None, np.mean(self.all_reward_sums, axis=0), self.rf + 'training.html')
