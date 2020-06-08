# SR algorithm libraries
from agents.fisr_agent_q import QLearningAgent
from report.pro_report import Report
from production.pclass import Production
from production.penv import PFisrEnvironment

# Python libraries
import numpy as np
import pandas as pd
from tqdm import trange
import time


# ----------------------------------------------------------
# Pablo Alejandro Parra Gómez
# pa.parra12@uniandes.edu.co
# Universidad de Los Andes, Colombia.
# Mayo, 2020
# ----------------------------------------------------------

# ##########################################################
# Update before use
q = pd.read_feather('E:/pg_fisr/data/123_06022020_nsimulation/q_ieee123_1r_200e.ftr')
term_states = pd.read_feather('E:/pg_fisr/data/123_06022020_nsimulation/term_states_dss2g.ftr').to_numpy()
# ----------------------------------------------------------
report_folder = "E:/pg_fisr/report/"
# ##########################################################

env = PFisrEnvironment(term_states)
agent = QLearningAgent(0)
num_switches = env.opendss_g.num_switches
num_lines = env.opendss_g.num_lines

# q values info
q_values = []
for i, sw in enumerate(env.opendss_g.switches):
    q_values.append(q[sw].to_list())

q_values = np.asarray(q_values).transpose()

# -------------------------------------------
# Production
# -------------------------------------------
all_actions = []
num_actions = []
action_times = []
lines_to_fail = env.opendss_g.lines

for i in trange(env.opendss_g.num_lines):
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
