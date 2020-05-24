from rl_code.training.com import OpenDSSCOM
from rl_code.training.fisr_env import FisrEnvironment
from rl_code.fisr_agent_q import QLearningAgent
from rl_code.training.tclass import Training
from report.train_report import Report
from data.simulation import DataSimulation
import pandas as pd
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
input('Press Enter to continue...')
print('''
Let´s start:
First, declare the rl parameters  
''')
t_epi = int(input('Number of episodes?'))
t_runs = int(input('Number of runs?'))
path = input('Now, OpenDSS model path:')
data_simulated = int(input('1. Data from env - 2. Simulated data '))

voltages = None
iso_loads = None
term_states = None

# ----------------------------------------------------------
this_path = os.getcwd()
report_folder = f'{this_path}/report/'

# Object initialization
com = OpenDSSCOM(path)
if data_simulated == 2:
    voltages = pd.read_feather(input('Enter voltages path:')).to_numpy()
    iso_loads = pd.read_feather(input('Enter currents path:')).to_numpy()
    term_states = pd.read_feather(input('Enter isolated loads path')).to_numpy()
elif data_simulated == 1:
    ds = DataSimulation(f'{this_path}/data/', com)
    voltages, currents, iso_loads = ds.get_data()
    term_states = ds.get_terminal_states(iso_loads, voltages)

circuit_name = com.DSSCircuit.Name
env = FisrEnvironment(com, voltages, iso_loads, term_states)
agent = QLearningAgent(1)

# Training
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

# Report generation
report = Report('training.html', s_df, t_df, report_folder)
report.make_report()

# Save q_values
df_q = pd.DataFrame(data=training.agent.q, columns=com.switches)
df_q.to_feather(f'{this_path}/data/q_{circuit_name}_{t_runs}r_{t_epi}e.ftr')

# 'E:\pg_fisr\models\IEEE_123_FLISR_Case\Master.dss'
#'E:/123bus_voltages_2020-05-16.ftr'
#'E:/123bus_isolated_loads_2020-05-16.ftr'
# 'E:/ieee123bus_terminal_states_2020-05-16.ftr'

#'E:/pg_fisr/models/ieee33bus.dss'