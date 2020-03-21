
import numpy as np
from scipy.special import comb
from itertools import combinations
from dissystem import DistributionSystem
from fisr_env import FisrEnvironment

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
switches_conn = [('N0','N1'), ('N1','N2'),('N1','N3'),('N2','N4'),('N3','N4'),('N4','N5')]
switches = ['S1', 'S2', 'S3', 'S6', 'T4', 'T5']
tie = ['T4', 'T5']

bus33 = DistributionSystem(nodes, switches, tie, switches_conn)
bus33.sys_start()
sw = bus33.switches_name
f = bus33.switches_obs
b = bus33.opened_switches
c = bus33.closed_switches

print(sw, f, b, c)

names = bus33.get_switches_names(b)
print(names)

adj = bus33.create_adjacency_matrix()
print(adj)

# h = bus33.possible_open_actions([1])
# print(h)

# print('--------------------------')
# env = FisrEnvironment()
# obs = env.get_observation()
# print(obs)