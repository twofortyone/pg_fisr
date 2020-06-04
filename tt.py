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
# path = 'E:/pg_fisr/models/IEEE_8500_Bus-G/Master.DSS' # IEEE 8500 Node Test Feeder
path = 'E:/pg_fisr/models/IEEE_123_FLISR_Case/Master.dss'  # IEEE 123 Node Test Feeder
#path = 'E:/pg_fisr/models/ieee33bus.dss' # IEEE 33 Node Test Feeder
# ----------------------------------------------------------
this_path = os.path.abspath(os.path.dirname(__file__))
report_folder = f'{this_path}/report/'

# ##########################################################
t0 = time.time()
com = OpenDSSCOM(path)
# 'E:/pg_fisr/data/33bus_training06022020_new_simultation/'
voltages = pd.read_feather('E:/pg_fisr/data/123_06022020_nsimulation/ieee123bus_voltages_2020-06-02.ftr').to_numpy()
iso_loads = pd.read_feather('E:/pg_fisr/data/123_06022020_nsimulation/ieee123bus_isolated_loads_2020-06-02.ftr').to_numpy()
num_loops = pd.read_feather('E:/pg_fisr/data/123_06022020_nsimulation/ieee123bus_num_loops_2020-06-02.ftr').to_numpy()

#voltages = pd.read_feather('E:/pg_fisr/data/33bus_training06022020_new_simultation/ieee37bus_voltages_2020-06-02.ftr').to_numpy()
#iso_loads = pd.read_feather('E:/pg_fisr/data/33bus_training06022020_new_simultation/ieee37bus_isolated_loads_2020-06-02.ftr').to_numpy()
#num_loops = pd.read_feather('E:/pg_fisr/data/33bus_training06022020_new_simultation/ieee37bus_num_loops_2020-06-02.ftr').to_numpy()



circuit_name = com.DSSCircuit.Name
env = FisrEnvironment(com, voltages, iso_loads, num_loops)
term_states = pd.read_feather('E:/pg_fisr/data/123_06022020_nsimulation/ieee123bus_terminal_states_2020-06-02.ftr').to_numpy()
#term_states = pd.read_feather('E:/pg_fisr/data/33bus_training06022020_new_simultation/ieee37bus_terminal_states_2020-06-02.ftr').to_numpy()
env.terminal_states = term_states
agent = QLearningAgent(1)
# ------------------------------------------
# Training
# ------------------------------------------
print('Training model ...')
training = Training(env, agent, report_folder)
train_path = training.run_training(t_runs, t_epi)
t1 = time.time()

# System info
data_system, ds_label = env.save_system_data(f'{this_path}/data/data_{circuit_name}.xlsx')
data_label = ['Circuit:', '# Lines', '# Switches', '# Loads']
s_df = pd.DataFrame(data_system[0:4], data_label, ['Values'])  # System data frame

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
print('Validating model ...')
agent_pro = QLearningAgent(0)
env_pro = FisrEnvironment_Pro(com, voltages, iso_loads, num_loops)
env_pro.terminal_states = term_states
all_actions = []
all_restored_data = []
num_actions = []
action_times = []
lines_to_fail = com.lines

for i in trange(com.num_lines):  # for closed switches
    production = Production(env_pro, agent_pro, agent.q, i, report_folder)
    t2 = time.time()
    pro = production.run_production(1, 1)
    t3 = time.time()
    all_actions.append(pro[1])
    all_restored_data.append(pro[2][0])
    num_actions.append(len(pro[1]))
    action_times.append(round(t3-t2, 3))


# -------------------------------------------
# Report
# -------------------------------------------

# Actions data frame
#list_of_acts = [x for x in all_actions]
actions_df = pd.DataFrame(data=lines_to_fail, columns=['Faulted line'])
actions_df.insert(1, 'Actions', all_actions, True)
actions_df.insert(2, 'No. of Actions', num_actions, True)
actions_df.insert(3, 'Time elapsed [s]', action_times, True)
list_prev_nil = [x[0][0] for x in all_restored_data]
list_nil = [x[1][0] for x in all_restored_data]
list_vol = [x[2] for x in all_restored_data]
actions_df.insert(4, 'No. of IL pre SR', list_prev_nil, True)
actions_df.insert(5, 'No. of IL post SR', list_nil, True)
res_percent = [x[0][0] for x in all_restored_data] #(x[0]-x[1])/x[0]
actions_df.insert(6, 'Restoration Rate', res_percent)

actions_df.to_excel(f'{report_folder}actions_{circuit_name}.xlsx')

statistics = actions_df.describe()  # Statistics data frame

# Report generation
report = Report(report_folder, 'training.html', actions_df, statistics, s_df, t_df)
report.make_report()
