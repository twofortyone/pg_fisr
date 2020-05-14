import numpy as np
import pandas as pd
from tqdm import trange
from itertools import product

from rl_code.dissystem import DistributionSystem

system = DistributionSystem()
num_switches = system.num_switches
switch_state = [0, 1]
switch_states = list(product(switch_state, repeat=num_switches))
ss_arrray = np.asarray(switch_states)

num_lines = system.num_lines
states = np.zeros((num_lines*(2**num_switches), num_switches))

voltages = []
prev_state = None
for i in trange(num_lines):
    system.failure_line(i)
    for j in trange(len(ss_arrray)):
        state = ss_arrray[j, :]
        voltage = system.opendssg.get_voltage_magpu()
        voltages.append(voltage)
        pos = np.where(state != prev_state)[0]
        for position in pos:
            system.operate_switch(position, state[position])
        prev_state = state
    system.fix_failure(i)

beta = np.asarray(voltages)
alfa = beta.transpose()
labels = [str(x) for x in range(len(states))]
df_voltages = pd.DataFrame(data=alfa[0], columns=labels)
df_voltages.to_feather('E:/123bus_voltages.ftr')
