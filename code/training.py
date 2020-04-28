from rl_code.fisr_env import FisrEnvironment
from rl_code.fisr_agent import QLearningAgent
from rl_code.train_pro import Training
import pandas as pd
from report.train_report import Report
import time


name = 'IEEE 33 BUS Test Case'

# ##########################################################
# Update before use
ties = 3
time_steps = 9
t_epi = 1
t_runs = 1
# ----------------------------------------------------------
path = 'E:\ieee33bus37.dss'
report_folder = "E:/pg_fisr_develop/code/report/"
voltages_ftr = f'E:/data/{ties}ties_voltages.ftr'
# ##########################################################

env = FisrEnvironment(path, ties, voltages_ftr, time_steps)
agent = QLearningAgent()
# ------------------------------------------
# Training
# ------------------------------------------
t0 = time.time()
training = Training(env, agent, report_folder)
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
q_values = training.agent.q
states = [str(x) for x in training.env.states]
actions = [str(x) for x in training.env.actions]

# -------------------------------------------
# Report
# -------------------------------------------
# System data frame
s_df = pd.DataFrame(data_system, ds_label, ['Values'])

# Training data frame
t_df = pd.DataFrame(data_training, dt_label, ['Values'])

# Report generation
report = Report(train_path, s_df, t_df, report_folder)
report.make_report()

# Save q_values
df_q = pd.DataFrame(data=agent.q, columns=actions)
df_q.to_feather(f'E:/q_{ties}ties_{t_runs}r_{t_epi}e_{time_steps}ts_nr_woopendss.ftr')

