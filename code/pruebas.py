
import numpy as np
from scipy.special import comb
from itertools import combinations
from dissystem import DistributionSystem

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


states = start_state(2, 6)

#index = states.index((3,4,5,6,7))
#print(index)

nodes = ['N0', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6']
switches = ['S1', 'S2', 'S3', 'S6', 'T4', 'T5']
tie = ['T4', 'T5']

bus33 = DistributionSystem(nodes, switches, tie)
bus33.sys_start()
sw = bus33.switches_name
close = bus33.possible_close_actions(3)
for i in close:
    print(sw[i])

f = bus33.switches_obs
b = bus33.get_opened_switches()
c = bus33.get_closed_switches()

print(b, c)

d = bus33.possible_close_actions(1)
print(d)

names = bus33.get_switches_names(b)

print(names)

