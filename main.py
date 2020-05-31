from data.simulation import DataSimulation
from rl_code.training.fisr_env import FisrEnvironment
from rl_code.fisr_agent_q import QLearningAgent
from rl_code.training.tclass import Training
from rl_code.training.t_pclass import Production
from rl_code.training.com import OpenDSSCOM
from rl_code.training.t_env_pro import FisrEnvironment_Pro
import pandas as pd
from report.report import Report
from tqdm import trange
import time
import os

# ----------------------------------------------------------
# Pablo Alejandro Parra Gómez
# pa.parra12@uniandes.edu.co
# Los Andes University, Colombia.
# Mayo, 2020
# ----------------------------------------------------------
print('''
============================================================
|       Welcome to Service Restoration RL Algorithm        | 
============================================================
''')
t_epi = 200
t_runs = 1
path = 'E:/pg_fisr/models/ieee33bus.dss'
# ----------------------------------------------------------
this_path = os.path.abspath(os.path.dirname(__file__))
report_folder = f'{this_path}/report/'

# ##########################################################

com = OpenDSSCOM(path)
ds = DataSimulation(f'{this_path}/data/', com)
voltages, currents, iso_loads = ds.get_data()
term_states = ds.get_terminal_states(iso_loads, voltages)

circuit_name = com.DSSCircuit.Name
env = FisrEnvironment(com, voltages, iso_loads, term_states)
agent = QLearningAgent(1)
# ------------------------------------------
# Training
# ------------------------------------------
t0 = time.time()
training = Training(env, agent, report_folder)
train_path = training.run_training(t_runs, t_epi)
t1 = time.time()

# System info
data_system, ds_label = env.save_system_data(f'{this_path}/data/data_{circuit_name}.xlsx')
s_df = pd.DataFrame(data_system[0:3], ds_label[0:3], ['Values'])  # System data frame

# Training info
t_time = round(t1-t0, 2)
data_training = [env.num_states, env.num_actions, str(t_epi), str(t_runs), str(t_time) + ' seconds']
dt_label = ['States:', 'Actions:', 'Episodes:', 'Runs:', 'Time elapsed:']
t_df = pd.DataFrame(data_training, dt_label, ['Values'])  # Training data frame

# Save q_values
df_q = pd.DataFrame(data=training.agent.q, columns=com.switches)
df_q.to_feather(f'{this_path}/data/q_{circuit_name}_{t_runs}r_{t_epi}e.ftr')

# -------------------------------------------
# Production
# -------------------------------------------
agent_pro = QLearningAgent(0)
env_pro = FisrEnvironment_Pro(com, voltages, iso_loads, term_states)

all_actions = []
num_actions = []
action_times = []
lines_to_fail = com.lines[1:]

for i in trange(1, com.num_lines):  # for closed switches
    production = Production(env_pro, agent_pro, agent.q, i, report_folder)
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
actions_df = pd.DataFrame(data=lines_to_fail, columns=['Failure'])
actions_df.insert(1, 'Actions', list_of_acts, True)
actions_df.insert(2, 'Number of actions', num_actions, True)
actions_df.insert(3, 'Time elapsed', action_times, True)

statistics = actions_df.describe()  # Statistics data frame

# Report generation
report = Report(report_folder, 'training.html', actions_df, statistics, s_df, t_df)
report.make_report()
