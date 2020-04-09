from fisr_env import FisrEnvironment
from fisr_agent import QLearningAgent
from train_pro import Training
from train_pro import Production
import pandas as pd
from report import Report
from tqdm import tqdm

env = FisrEnvironment()
agent = QLearningAgent()

# ------------------------------------------
# Training
# ------------------------------------------
training = Training(env, agent)
train_path = training.run_training(1, 20)

q_values = training.agent.q

states = [str(x) for x in training.env.states]
actions = [str(x) for x in training.env.actions]

# -------------------------------------------
# Production
# -------------------------------------------
all_actions = []
num_actions = []
switches = env.system.system_data.switches


for i in tqdm(range(len(switches)-2)):  # for closed switches
    production = Production(env, agent, q_values, i)
    pro = production.run_production(1, 1)
    all_actions.append(pro[1])
    num_actions.append(len(pro[1]))

# -------------------------------------------
# Report
# -------------------------------------------
list_of_acts = [str(x) for x in all_actions]
df = pd.DataFrame(data=switches[0:32], columns=['Failure'])
df.insert(1, 'Actions', list_of_acts, True)
df.insert(2, 'Number of actions', num_actions, True)
statistics = df.describe()
report = Report(train_path, train_path, df, statistics)
report.make_report()
