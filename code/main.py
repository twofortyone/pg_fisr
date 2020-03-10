import cominterface
import circuit
import numpy as np
com = cominterface.Opendss('D:\Bus_37\ieee37.dss')
#print(com.get_path(), com.get_version())

com.solve()
#com.send_command('show Voltages LN Nodes')

voltages = com.get_bus_vmag()
names = com.get_bus_names()
pu = com.get_bus_vmagpu()
pu = np.asarray(pu)
# pu = np.reshape(pu, (39, 3))

rest = circuit.Circuit(pu)
valor = rest.check_voltages_limits()
print(voltages)
print(pu)
print(names)
