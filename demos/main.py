from rl_code.opendss import Circuit
import numpy as np

path = 'D:\Bus_37\ieee37.dss'
# print(com.get_path(), com.get_version())
# com.send_command('show Voltages LN Nodes')

circuit = Circuit(path)
lines = circuit.get_lines()
index = 0

# for i in lines:
#     circuit.open_switch(i, 1)
#     circuit.open_switch(i, 2)
#     if index >= 1:
#         circuit.close_switch(lines[index-1], 1)
#         circuit.close_switch(lines[index-1], 2)
#
#     index += 1
#     voltage_limit_status = circuit.check_voltages_limits()
#     print(voltage_limit_status)

# loads = circuit.get_loads()
# print(loads)
voltage = circuit.get_voltages_pu()
print(voltage)

circuit.set_active_load('s730c')
print(circuit.get_ae_data())

circuit.open_switch('l6', 1)
# print(circuit.get_voltages_pu())

circuit.set_active_load('s730c')
print(circuit.get_ae_data())

print(circuit.num_load_offline())

print(circuit.get_buses())

# circuit.com.send_command('show voltages LN Nodes')
# circuit.com.send_command('show currents elements')

# circuit.open_switch('l1', 2)
# print(circuit.get_voltages_pu())

# print(circuit.get_ae_name())
# print(circuit.get_ae_buses())
# print(circuit.is_line_open('l1', 1))
#
# print(circuit.get_loadsbuses())

# bus_voltages_pu = circuit.get_voltages_pu()
# bus_voltages_pu = np.reshape(bus_voltages_pu, (39, 3))

# Algoritmo para obtner conn
lines = circuit.get_lines()
conn = np.array([])
for x in np.nditer(lines):
    circuit.set_active_line(str(x))
    nodes = circuit.get_ae_buses()
    for y in nodes:
        conn = np.append(conn, (y.split('.'))[0])

conn = np.reshape(conn, (-1, 2))

conn2 = []
for x in lines:
    circuit.set_active_line(x)
    nodes2 = circuit.get_ae_buses()
    aux = []
    for y in nodes2:
        aux.append(y.split('.')[0])
    conn2.append(aux)


