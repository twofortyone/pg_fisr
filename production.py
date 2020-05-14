from rl_code.production.fisr_env_pro import FisrEnvironment
from rl_code.fisr_agent_q import QLearningAgent
from rl_code.production.pclass import Production
import pandas as pd
from report.pro_report import Report
from tqdm import tqdm, trange
import time

# ##########################################################
# Update before use
ties = 12
time_steps = 700
t_epi = 100
t_runs = 1
# ----------------------------------------------------------
report_folder = "E:/pg_fisr/report/"
# ##########################################################

env = FisrEnvironment(time_steps)
agent = QLearningAgent(0)
num_switches = env.opendss_g.num_switches
num_lines = env.opendss_g.num_lines

# q values info
q = pd.read_feather(f'E:/q_{ties}ties_{t_runs}r_{t_epi}e_{time_steps}ts_intento1.ftr')
#q = pd.read_feather('E:/q_3nuevo.ftr')

q_values = q.to_numpy()

# -------------------------------------------
# Production
# -------------------------------------------
all_actions = []
num_actions = []
action_times = []
lines_to_fail = env.opendss_g.lines

for i in trange(num_lines):  # for closed switches
    production = Production(env, agent, q_values, i, report_folder)
    t2 = time.time()
    pro = production.run_production(1, 1)
    t3 = time.time()
    all_actions.append(pro[1])
    num_actions.append(len(pro[1]))
    action_times.append(round(t3-t2, 3))
# -------------------------------------------
# Report
# -------------------------------------------
actions = env.opendss_g.switches

# Actions data frame
list_of_acts = [str(x) for x in all_actions]
actions_df = pd.DataFrame(data=lines_to_fail, columns=['Failure'])
actions_df.insert(1, 'Actions', list_of_acts, True)
actions_df.insert(2, 'Number of actions', num_actions, True)
actions_df.insert(3, 'Time elapsed', action_times, True)
# Statistics data frame
statistics = actions_df.describe()

# Report generation
report = Report(actions_df, statistics, report_folder)
report.make_report()

# Save q_values
df_q = pd.DataFrame(data=agent.q, columns=actions)
df_q.to_feather('E:/q_3nuevo.ftr')
