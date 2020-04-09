from fisr_env import FisrEnvironment
from fisr_agent import QLearningAgent
from noname import Training
from noname import Production
import numpy as np
import pandas as pd
from report import Report

env = FisrEnvironment()
agent = QLearningAgent()

# ------------------------------------------
# Training
# ------------------------------------------
training = Training(env, agent)
train_path = training.run_training(1, 50)

q_values = training.agent.q

#states = [str(x).strip('[]').replace(',', '') for x in training.env.states]
#actions = [str(x).strip('[]').replace(',', '') for x in training.env.actions]

states = [str(x) for x in training.env.states]
actions = [str(x) for x in training.env.actions]

# -------------------------------------------
# Production
# -------------------------------------------
# TODO: Must be in the range of closed switches (see whats happens with open sw)
all_actions = []
num_actions = []
switches = env.system.system_data.switches
# pro_path = None  # Todo: Delete propath from cicle

for i in range(len(switches)-2):
    production = Production(env, agent, q_values, i)
    pro = production.run_production(1, 1)
    #pro_path = pro[0]
    #print(pro[0])
    #print((pro[1]))
    #print('############################################', i)
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

#nodes = pro.env.system.system_data.nodes
#df = pd.DataFrame(data=nodes, columns=['Nodo fallado'])
#qdf = pd.DataFrame(q_values, index=states, columns=actions)
print('hola')
report = Report(train_path, train_path, df, statistics)
report.make_report()
