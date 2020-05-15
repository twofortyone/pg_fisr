import numpy as np
import pandas as pd
from packaging.markers import Op
from tqdm import trange
from itertools import product

from rl_code.training.com import OpenDSSCOM

system = OpenDSSCOM('E:\pg_fisr\models\IEEE_123_FLISR_Case\Master.dss')
num_switches = system.num_switches
switch_state = [0, 1]
switch_states = list(product(switch_state, repeat=num_switches))
ss_arrray = np.asarray(switch_states)

num_lines = system.num_lines
states = np.zeros((num_lines*(2**num_switches), num_switches))

voltages = []
prev_state = None
for line in trange(num_lines):
    system.fail_line(line)
    for j in range(len(ss_arrray)):
        state = ss_arrray[j, :]
        positions = np.where(state != prev_state)[0]
        for pos in positions:
            if state[pos] == 1: system.close_switch(pos)
            else: system.open_switch(pos)
        prev_state = state
        system.solve()
        voltage = system.get_voltage_magpu().tolist()
        voltages.append(voltage)
    system.failure_restoration(line)

beta = np.asarray(voltages)
alfa = beta.transpose()
labels = [str(x) for x in range(len(states))]
df_voltages = pd.DataFrame(data=alfa, columns=labels)
df_voltages.to_feather('E:/123bus_voltages.ftr')
