import numpy as np
import pandas as pd
from tqdm import trange
from itertools import product
import datetime


class DataSimulation:
    def __init__(self, path, open_dss):
        self.opendss = open_dss
        self.path = path
        self.circuit_name = self.opendss.DSSCircuit.Name
        num_switches = self.opendss.num_switches
        switch_state = [0, 1]
        switch_states = list(product(switch_state, repeat=num_switches))
        self.ss_array = np.asarray(switch_states)
        self.num_switch_states = len(switch_states)
        self.num_lines = self.opendss.num_lines

    def get_data(self):
        voltages = []
        num_isolated_loads = []
        currents = []
        num_loops = []
        for line in trange(self.num_lines):
            for j in range(self.num_switch_states):
                self.opendss.fail_line(line)  # failure current line
                state = self.ss_array[j, :]
                positions = np.where(state != self.opendss.start_status)[0]
                for pos in positions:
                    if state[pos] == 1:
                        self.opendss.close_switch(pos)
                    else:
                        self.opendss.open_switch(pos)
                self.opendss.solve()  # Updates previous changes
                num_loops.append(self.opendss.topology())  # Save number of loops
                voltages.append(get_num_voltage_violations(self.opendss.get_voltage_magpu()))  # Save voltages
                num_isolated_loads.append(self.opendss.get_num_isolated_loads())  # Save number of isolated loads
                #currents.append(self.opendss.get_currents())  # Save currents
                self.opendss.clear_run()
            #self.opendss.failure_restoration(line)  # restore current failure
        # Save data
        save_to_feather(self.path, self.circuit_name, voltages, 'voltages', 1)
        # save_to_feather(self.path, self.circuit_name, currents, 'currents', len(currents[0]))
        save_to_feather(self.path, self.circuit_name, num_isolated_loads, 'isolated_loads', 1)
        save_to_feather(self.path, self.circuit_name, num_loops, 'num_loops', 1)
        return [voltages, num_isolated_loads, num_loops]

    def get_terminal_states(self, env, nils, vs, loops):

        terminal_states = []
        prev_state = 0
        for line in trange(self.num_lines):
            env.opendss.fail_line(line)  # failure current line
            env.failure = line
            terminal = line * self.num_switch_states + env.get_default_state()
            print(f'falla en: {line}; state: {terminal}')
            prev_state = self.ss_array[env.get_ss_pos(terminal), :]
            reference = self.ss_array[env.get_ss_pos(terminal), :]
            prev_num_trans = None
            aux = 0
            for switch_state in range(self.num_switch_states):
                state = self.ss_array[switch_state, :]
                positions = np.where(state != prev_state )[0]
                check_trans = np.where(state != reference)[0]
                num_trans = check_trans.shape[0]
                for pos in positions:
                    if state[pos] == 1:
                        env.opendss.close_switch(pos)
                    else:
                        env.opendss.open_switch(pos)

                current_state = line * self.num_switch_states + switch_state
                prev_nil = nils[terminal]
                nil = nils[current_state]
                prev_num_vv = get_num_voltage_violations(np.asarray(vs[terminal]))
                num_vv = get_num_voltage_violations(np.asarray(vs[current_state]))
                prev_nloops = loops[terminal]
                nloops = loops[current_state]
                #print(f'cs: {current_state}; prev: {prev_nil} nil: {nil}; prev: {prev_num_vv}; numvv: {num_vv}; loops: {nloops}')
                if (nil < prev_nil) and nloops == 0:
                    terminal = current_state
                    print(f'----{terminal}; {nil}')
                    aux += 1
                    prev_num_trans = check_trans.shape[0]
                elif nil == prev_nil and aux != 0 and nloops == 0:
                    if (num_trans < prev_num_trans):
                        #if num_vv < prev_num_vv:  # todo: add current limits
                        terminal = current_state
                        print(f'menor numvv {terminal}; {prev_num_trans} -{num_trans}' )
                        prev_num_trans = check_trans.shape[0]
                prev_state = self.ss_array[env.get_ss_pos(current_state),:]
            terminal_states.append(terminal)
            print(f'queda con: {terminal}')
        save_to_feather(self.path, self.circuit_name, terminal_states, 'terminal_states', 1)
        return terminal_states


def get_num_voltage_violations(v):
    violations = v[(v > 0.1) & (v <= 0.95) | (v >= 1.05)]
    return violations.shape[0]


def save_to_feather(path, circuit_name, data, name, num_columns):
    date = datetime.date.today()
    labels = [str(x) for x in range(num_columns)]
    df_data = pd.DataFrame(data=data, columns=labels)
    df_data.to_feather(f'{path}/{circuit_name}bus_{name}_{date}.ftr')
