
# from opendss import OpenDSSCircuit
import numpy as np
#
# c = OpenDSSCircuit()
# v = c.com.get_voltage_magpu()
# vn = np.asarray(v).reshape((-1, 3))

from dissystem import DistributionSystem
sys = DistributionSystem()
sys.sys_start()



