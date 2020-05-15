from rl_code.training.fisr_env import FisrEnvironment
from rl_code.fisr_agent_q import QLearningAgent
from rl_code.training.tclass import Training
import pandas as pd
from report.train_report import Report
import time


name = 'IEEE 33 BUS Test Case'

# ##########################################################
# Update before use
ties = 12
time_steps = 10000
t_epi = 50
t_runs = 1
v_ftr = 1  # 1 if voltages are simulated, 0 otherwise
# ----------------------------------------------------------
path = 'E:\pg_fisr\models\IEEE_123_FLISR_Case\Master.dss'
report_folder = "E:/pg_fisr/report/"
# ##########################################################
t2 = time.time()
env = FisrEnvironment(path, time_steps, v_ftr)
t3 = time.time()
agent = QLearningAgent(1)
# ------------------------------------------
# Training
# ------------------------------------------
t0 = time.time()
training = Training(env, agent, report_folder)
t1 = time.time()
train_path = training.run_training(t_runs, t_epi)
t4 = time.time()
#print(f'{t1-t0}; et: {t3-t2}; at: {t0-t3}; training: {t4-t1}')

# System info
num_nodes = len(env.opendss.buses)
num_switches = env.opendss.num_switches
data_system = [name, num_nodes, num_switches]
ds_label = ['Name:', 'Nodes:', 'Switches:']

# Training info
t_time = round(t1-t0, 2)
num_states = str(len(env.states))
num_actions = str(len(env.actions))
data_training = [num_states, num_actions, str(t_epi), str(t_runs), str(t_time) + ' seconds']
dt_label = ['States:', 'Actions:', 'Episodes:', 'Runs:', 'Time elapsed:']

# q values info
q_values = training.agent.q
actions = training.env.opendss.switches

# -------------------------------------------
# Report
# -------------------------------------------
# System data frame
s_df = pd.DataFrame(data_system, ds_label, ['Values'])
# Training data frame
t_df = pd.DataFrame(data_training, dt_label, ['Values'])
# Report generation
report = Report('training.html', s_df, t_df, report_folder)
report.make_report()

# Save q_values
df_q = pd.DataFrame(data=agent.q, columns=actions)
df_q.to_feather(f'E:/q_{ties}ties_{t_runs}r_{t_epi}e_{time_steps}ts_simulated.ftr')

