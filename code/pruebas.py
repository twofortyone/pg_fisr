
import numpy as np
from scipy.special import comb
from itertools import combinations
from dissystem import DistributionSystem
from fisr_env import FisrEnvironment
from dissystem import ToPython

def estados(tie, switches):
    num_estados = comb(switches, tie)
    estados = np.arange(num_estados)

    for i in estados:
        estados[i]= np.array([0,0,0,0])
    return num_estados


def start_state(tie, sw):
    switches = np.arange(1, sw + 1)
    states = list(combinations(switches, tie))
    return states


states = start_state(5,7)

index = states.index((3,4,5,6,7))
print(index)

# Modelamiento del sistema de distribucion
nodes = ['N0', 'N1', 'N2', 'N3', 'N4', 'N5']
conn = [('N0','N1'), ('N1','N2'),('N1','N3'), ('N4','N5'), ('N2','N4'),('N3','N4')]
switches = ['S1', 'S2', 'S3', 'S6', 'T4', 'T5']
tie = ['T4', 'T5']

system_data = ToPython(nodes, switches, tie, conn)
bus33 = DistributionSystem(system_data)
bus33.sys_start()

f = bus33.switches_obs
b = bus33.opened_switches
c = bus33.closed_switches

print(f, b, c)

adj = bus33.get_adj_matrix()
print(adj)

print(bus33.conn)

#for i in range(int(input('Number of iteractions'))):
#    f = input('ingrese falla')

# h = bus33.possible_open_actions([1])
# print(h)

# print('--------------------------')
# env = FisrEnvironment()
# obs = env.get_observation()
# print(obs)

# def possible_close_actions(self, current_):
#     switches = self.switches_obs
#     actions = []
#     for i in range(len(switches)):
#         if i != current_ and switches[i] == 0:
#             actions.append(i)
#     return actions
#
# def possible_open_actions(self, current_switches):
#     cs = current_switches
#     to_open = self.closed_switches.copy()
#     for i in cs:
#         if i in to_open:
#             to_open.remove(i)
#     return to_open


