from rl_code.fisr_env import FisrEnvironment
from rl_code.fisr_agent import QLearningAgent
from rl_code.train_pro import Production
import pandas as pd
from report.pro_report import Report
from tqdm import tqdm
import time


env = FisrEnvironment()
agent = QLearningAgent()
num_nodes = len(env.system.nodes_obs)
num_switches = len(env.system.switches_obs)
num_tie = len(env.system.start_tie_obs)

# q values info
q = pd.read_feather('E:\q_3nuevo.ftr')
q_values = q.to_numpy()

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
actions = [str(x) for x in env.actions]

# Actions data frame
list_of_acts = [str(x) for x in all_actions]
actions_df = pd.DataFrame(data=switches[2:num_switches-num_tie], columns=['Failure'])
actions_df.insert(1, 'Actions', list_of_acts, True)
actions_df.insert(2, 'Number of actions', num_actions, True)
actions_df.insert(3, 'Time elapsed', action_times, True)
actions_df.insert()
# Statistics data frame
statistics = actions_df.describe()

# Report generation
report = Report(actions_df, statistics)
report.make_report()

# Save q_values
df_q = pd.DataFrame(data=agent.q, columns=actions)
df_q.to_feather('E:\q_3nuevo.ftr')
