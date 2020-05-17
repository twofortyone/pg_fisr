import numpy as np
import pandas as pd
from tqdm import trange
from itertools import product
import datetime
from rl_code.training.com import OpenDSSCOM


class DataSimulation:
    def __init__(self, OpenDSSCOM, num_nodes):
        self.opendss = OpenDSSCOM
        self.num_nodes = num_nodes
        num_switches = self.opendss.num_switches
        switch_state = [0, 1]
        switch_states = list(product(switch_state, repeat=num_switches))
        self.ss_arrray = np.asarray(switch_states)
        self.num_switch_states = len(switch_states)
        self.num_lines = self.opendss.num_lines

    def get_data(self):
        voltages = []
        num_isolated_loads = []
        currents = []
        prev_state = None
        for line in trange(self.num_lines):
            self.opendss.fail_line(line)  # failure current line
            for j in range(self.num_switch_states):
                state = self.ss_arrray[j, :]
                positions = np.where(state != prev_state)[0]
                for pos in positions:
                    if state[pos] == 1:
                        self.opendss.close_switch(pos)
                    else:
                        self.opendss.open_switch(pos)
                prev_state = state
                self.opendss.solve()
                # Save voltages
                voltage = self.opendss.get_voltage_magpu().tolist()
                voltages.append(voltage)
                # Save number of isolated loads
                num_is = self.opendss.get_num_isolated_loads()
                num_isolated_loads.append(num_is)
                # Save currents
                current = self.opendss.get_currents()
                currents.append(current)
            self.opendss.failure_restoration(line)  # restore current failure
        # Save data
        save_to_feather(self.num_nodes, voltages, 'voltages', len(voltages[0]))
        save_to_feather(self.num_nodes, currents, 'currents', len(currents[0]))
        save_to_feather(self.num_nodes, num_isolated_loads, 'isolated_loads', 1)
        return [voltages, currents, num_isolated_loads]


def save_to_feather(num_buses, data, name, num_columns):
    date = datetime.date.today()
    labels = [str(x) for x in range(num_columns)]
    df_data = pd.DataFrame(data=data, columns=labels)
    df_data.to_feather(f'E:/{num_buses}bus_{name}_{date}.ftr')

com = OpenDSSCOM('E:\pg_fisr\models\IEEE_123_FLISR_Case\Master.dss')
DS = DataSimulation(com, 123)
voltages, currents, num_is = DS.get_data()
