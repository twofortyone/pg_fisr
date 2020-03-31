
import numpy as np
from scipy.special import comb
from itertools import combinations
from dissystem import DistributionSystem
from fisr_env import FisrEnvironment
from dissystem import OpenDSS2Python


class Prueba:

    def estados(tie, switches):
        num_estados = comb(switches, tie)
        estados = np.arange(num_estados)

        for i in estados:
            estados[i]= np.array([0,0,0,0])
        return num_estados


    # def start_state(tie, sw):
    #     switches = np.arange(1, sw + 1)
    #     states = tuple(combinations(switches, tie))
    #     return states
    #
    # states = start_state(5,7)
    #
    # index = states.index((3,4,5,6,7))
    # print(index)

    # Modelamiento del sistema de distribucion
    nodes = ['N0', 'N1', 'N2', 'N3', 'N4', 'N5']
    conn = [('N0','N1'), ('N1','N2'),('N1','N3'), ('N4','N5'), ('N2','N4'),('N3','N4')]
    switches = ['S1', 'S2', 'S3', 'S6', 'T4', 'T5']
    tie = ['T4', 'T5']

    system_data = OpenDSS2Python(nodes, switches, tie, conn)
    bus33 = DistributionSystem()


    f = bus33.switches_obs
    g = bus33.nodes_obs
    b = bus33.opened_switches
    c = bus33.closed_switches

    print(f, g, b, c)

    adj = bus33.get_adj_matrix()
    print(adj)

    print(system_data.switches)
    print(system_data.nodes)
    print(bus33.conn)

    print('-----------------------------')
    print('-----------------------------')

    for x in range(len(f)):
        bus33.do_failure(x)
        print('switches ', bus33.switches_obs)
        print('nodes ', bus33.nodes_obs)
        print('closed s ', bus33.closed_switches)
        print('opened ', bus33.opened_switches)
        print('nodes offline ', bus33.num_nodes_offline())
        print(bus33.nodes_adj_matrix)
        print()
        print('-----------------------------')
        bus33.close_switch(x)

# for i in range(int(input('Number of iteractions'))):
#    f = input('ingrese falla')

# h = bus33.possible_open_actions([1])
# print(h)

# print('--------------------------')
env = FisrEnvironment()
env.env_start()
obs = env.get_observation()
print(obs)
print(env.env_step(5))
# print(env.env_cleanup())

a = env.get_actions()
print(a)

