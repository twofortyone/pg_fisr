

import numpy as np
#inc = env.system.inc_matrix
#incpos = np.where(inc==-1,1, inc)
#degreevector = np.count_nonzero(incpos, axis=1)
#degreem = np.zeros((33,33))

#for i, x in enumerate(degreevector):
#    degreem[i,i] = x

g = np.array([[0., 0., 0., 0., 1., 0.],
              [0., 0., 1., 0., 0., 0.],
              [0., 1., 0., 0., 0., 0.],
              [0., 0., 0., 0., 0., 1.],
              [1., 0., 0., 0., 0., 0.],
              [0., 0., 0., 1., 0., 0.]])

degreev = degreevector = np.count_nonzero(g, axis=1)
degreem = np.zeros((6,6))

for i, x in enumerate(degreev):
    degreem[i,i] = x

from scipy.sparse import csgraph
l = csgraph.laplacian(g, normed=True)
e = np.around(np.linalg.eigvals(l), 1)
print(e)