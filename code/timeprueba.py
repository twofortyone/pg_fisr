
import numpy as np
import time
from sys import getsizeof

nodes = ['N0', 'N1', 'N2', 'N3', 'N4', 'N5']
conn = [('N0', 'N1'), ('N1', 'N2'), ('N1', 'N3'),
        ('N4', 'N5'), ('N2', 'N4'), ('N3', 'N4')]
switches = ['S1', 'S2', 'S3', 'S6', 'T4', 'T5']

nn = len(nodes)
ns = len(switches)

def find_pos(elements, element): return elements.index(element)

connnumpy = np.zeros((ns, 2))
sta = time.time()

for i in range(ns):
    for z in range(2):
        pos = find_pos(nodes, conn[i][z])
        connnumpy[i, z] = pos

eta = time.time() 

print('tiempo numpy = ', eta-sta)

connlist = []
stl = time.time()

for x in conn:
    pos = []
    for z in x:
        pos.append(find_pos(nodes, z))
        connlist.append(tuple(pos))
etl = time.time()

print('tiempo list = ', etl-stl)

# ------------------------------------------------------

stl = time.time()
z = [ x for x in range(1000000)]
etl = time.time()

sta = time.time()
n = np.arange(1000000)
eta = time.time()

print('numpy = ', eta-sta)
print('list = ', etl-stl)

stl = time.time()
u = np.asarray(z)
etl = time.time()

print('converts = ', etl-stl)
