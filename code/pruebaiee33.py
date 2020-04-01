
# from opendss import OpenDSSCircuit
import numpy as np
#
# c = OpenDSSCircuit()
# v = c.com.get_voltage_magpu()
# vn = np.asarray(v).reshape((-1, 3))

from dissystem import DistributionSystem
sys = DistributionSystem()
sys.sys_start()

a = np.arange(10)
b = np.array([1, 2, 3])
z = np.zeros((len(a)*len(b), 2))
for i in range(len(b)):
    z[i*len(a):i*len(a)+len(a), 0] = b[i]
    z[i * len(a):i * len(a) + len(a), 1] = a

pos = np.where(z[:, 0] == 2)
aux = pos[0]
d = z[pos, 1]
e = np.where(d[0, :] == 9)

cs = np.array([2, 4])
a = z
lista = []
# forward
for i in range(z.shape[1]):
    aux = a[:, i]
    pos = np.where(aux == cs[i])
    a = a[pos, :][0]
    lista.append(pos[0])

# backward
pos = 0
for i in range(z.shape[1]):
    pos = lista[z.shape[1]-1-i][pos]



