from fisr_env import FisrEnvironment
from fisr_agent import QLearningAgent
from noname import Training
from noname import Production
import numpy as np
import pandas as pd

env = FisrEnvironment()
agent = QLearningAgent()

training = Training(env, agent)
training.run_training(1, 50)

q_values = training.agent.q

production = Production(env, agent, q_values, 0)
production.run_production(1, 5)

nodes = production.env.system.system_data.nodes
df = pd.DataFrame(data=nodes, columns=['Nodo fallado'])

