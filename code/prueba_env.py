from fisr_env import FisrEnvironment
from scipy.special import comb
from fisr_agent import QLearningAgent
import numpy as np

from scipy.stats import sem
import matplotlib.pyplot as plt  # used 
from rl_glue import RLGlue  # used 
from tqdm import tqdm  # used 
import pickle

env = FisrEnvironment()
agent = QLearningAgent()
# all_reward_sums= {}
step_sizes = np.linspace(0.1,1.0,10)
# number of actions 
closed = env.system.closed_switches
opened = env.system.opened_switches
num_closed = len(closed)
num_opened = len(opened)
num_actions = num_closed * num_opened

# number of states
start_tie = env.system.start_tie_obs
switches_obs = env.system.switches_obs
num_tie = len(start_tie)
num_switches = len(switches_obs)
num_states = int(comb(num_switches, num_tie))


agent_info = {'num_actions': num_actions, 'num_states':num_states,
'epsilon': 0.1, 'discount':1.0, 'step_size': 0.5}
env_info = {}
num_runs = 10
num_episodes = 500
all_reward_sums = []
all_state_visits = []

for run in tqdm(range(num_runs)):
    agent_info['seed'] = run
    rl_glue = RLGlue(env, agent)
    rl_glue.rl_init(agent_info, env_info)

    reward_sums = []
    state_visits = np.zeros(num_states)
    for episode in range(num_episodes):
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

    all_reward_sums.append(reward_sums)
    all_state_visits.append(state_visits)

plt.plot(np.mean(all_reward_sums, axis=0), label='algorithm')
plt.xlabel("Episodes")
plt.ylabel("Sum of\n rewards\n during\n episode", rotation=0, labelpad=40)
#plt.xlim(0, 500)
#plt.ylim(-100, 0)
plt.legend()
plt.grid
plt.show()



print('Started successfully!')