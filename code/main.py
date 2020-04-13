from fisr_env import FisrEnvironment
from fisr_agent import QLearningAgent
from train_pro import Training
from train_pro import Production
import pandas as pd
from report import Report
from tqdm import tqdm
import time


name = 'IEEE 33 BUS Test Case'
env = FisrEnvironment()
agent = QLearningAgent()
t_epi = 200
t_runs = 1
# ------------------------------------------
# Training
# ------------------------------------------
t0 = time.time()
training = Training(env, agent)
train_path = training.run_training(t_runs, t_epi)
t1 = time.time()

# System info
num_nodes = len(env.system.nodes_obs)
num_switches = len(env.system.switches_obs)
num_tie = len(env.system.start_tie_obs)
data_system = [name, num_nodes, num_switches, num_tie]
ds_label = ['Name:', 'Nodes:', 'Switches:', 'Tie:']

# Training info
t_time = round(t1-t0, 2)
num_states = str(len(env.states))
num_actions = str(len(env.actions))
data_training = [num_states, num_actions, str(t_epi), str(t_runs), str(t_time) + ' seconds']
dt_label = ['States:', 'Actions:', 'Episodes:', 'Runs:', 'Time elapsed:']

# q values info
q_values = agent.q
states = [str(x) for x in env.states]
actions = [str(x) for x in env.actions]

# -------------------------------------------
# Production
# -------------------------------------------
all_actions = []
num_actions = []
action_times =[]
switches = env.system.system_data.switches

for i in tqdm(range(2, num_switches-num_tie)):  # for closed switches
    production = Production(env, agent, q_values, i)
    t2 = time.time()
    pro = production.run_production(1, 1)
    t3 = time.time()
    all_actions.append(pro[1])
    num_actions.append(len(pro[1]))
    action_times.append(round(t3-t2, 3))
# -------------------------------------------
# Report
# -------------------------------------------

# Actions data frame
list_of_acts = [str(x) for x in all_actions]
actions_df = pd.DataFrame(data=switches[2:num_switches-num_tie], columns=['Failure'])
actions_df.insert(1, 'Actions', list_of_acts, True)
actions_df.insert(2, 'Number of actions', num_actions, True)
actions_df.insert(3, 'Time elapsed', action_times, True)

# Statistics data frame
statistics = actions_df.describe()

# System data frame
s_df = pd.DataFrame(data_system, ds_label, ['Values'])

# Training data frame
t_df = pd.DataFrame(data_training, dt_label, ['Values'])

# Report generation
report = Report(train_path, actions_df, statistics, s_df, t_df)
report.make_report()

# Save q_values
df_q = pd.DataFrame(data=agent.q, columns=actions)
df_q.to_feather('E:\q_3tie_1r_50e_2000ts.ftr')
