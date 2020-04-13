from fisr_env import FisrEnvironment
import numpy as np
import pandas as pd
from tqdm import tqdm, trange


env = FisrEnvironment()
states = env.states  # numpy array
prev_state = env.get_observation()  # int
nodes = env.system.num_nodes


def close_switch(switch):
    env.system.close_switch(switch)


def open_switch(switch):
    env.system.open_switch(switch)


def oper_state(state):
    switches = states[prev_state]
    for x in switches:
        close_switch(x)

    switches = states[state]
    for x in switches:
        open_switch(x)
    env.system.system_solver()
    return state


vol = np.arange(nodes)
vol = vol.reshape(nodes, 1)
df_voltages = pd.DataFrame(data=vol, columns=['index'])
for i in tqdm(range(0, len(states))):
    prev_state = oper_state(i)
    voltages = env.system.system_data.open_dss.get_voltage()
    #vol = np.hstack((vol, voltages))
    for j in range(1, 4):
        index = j+(i*3)
        df_voltages.insert(loc=index, column=str(index), value=voltages[:, j-1])
    #vol = np.append(vol, voltages, axis=1)

labels = [str(x) for x in range(len(states)*3)]

#df_voltages = pd.DataFrame(vol[:, 1:], columns=labels)
df_voltages.to_feather('E:/5ties_voltages.ftr')
