from fisr_env import FisrEnvironment
from fisr_agent import QLearningAgent
from noname import Training
from noname import Production

env = FisrEnvironment()
agent = QLearningAgent()

training = Training(env, agent)
training.run_training(1, 50)

q_values = training.agent.q

production = Production(env, agent, q_values, 0)
production.run_production(1, 5)
