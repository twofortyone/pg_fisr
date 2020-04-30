# -*- coding: utf-8 -*-
"""
Created on Mon Oct 01 2018

@author: AC Melhorn

This file is just an example of working with the openDSSGTCP module/class. In 
order to run this file OpenDSS-G needs to be open with the IEEE 34 Nodes test
case in simulation mode.  If a different circuit is open then the getElement*
functions need to change to elements in the circuit being simulated.

The python code should print the bus names, node names, and the pu voltage 
magnitude in the command prompt.  It will also save the pu voltage magnitude
and voltage magnitudes and angles in seperate *.csv files.
"""

import numpy as np
import openDSSGTCP as dssTCP

# may need to chnage setting for individual setup
TCP_IP = '127.0.0.1'
TCP_PORT = 6345
BUFFER_SIZE = 20000

ODGTCP = dssTCP.OpenDSSGTCP(TCP_IP, TCP_PORT, BUFFER_SIZE)

ODGTCP.startTCPConnection()

#data = ODGTCP.stepIn()
#print data

# get and print bus names
bus_names = ODGTCP.getBusNames()
print(bus_names)
#
# get and print node names
node_names = ODGTCP.getNodeNames()
print(node_names)
#
# # get and print pu voltage magnitudes
voltage_pu = ODGTCP.getVoltsPU()
print(voltage_pu)

# get voltage magnitudes and angles
voltage = ODGTCP.getVolts()

# format pu voltage magnitudes, and voltage magnitudes and angles
#voltage_pu_formated_data = dssTCP.formatDataThreePhase(bus_names, node_names, voltage_pu)
#voltage_formated_data = dssTCP.formatComplexDataThreePhase(bus_names, node_names, voltage)
#
# # save the voltages to *.csv files
# np.savetxt("nodeVoltagesPU_TCP.csv", voltage_pu_formated_data, delimiter=",", fmt='%s')
# np.savetxt("nodeVoltages_TCP.csv", voltage_formated_data, delimiter=",", fmt='%s')

#
# # get and print voltages, powers, and currents for element 812-814
# voltage_812 = ODGTCP.getElementVoltage('812-814', 1)
# print(voltage_812)
# voltage_814 = ODGTCP.getElementVoltage('812-814', 2)
# print(voltage_814)
# powers_812_814 = ODGTCP.getElementPowers('812-814')
# print(powers_812_814)
# currents_812_814 = ODGTCP.getElementCurrents('812-814')
# print(currents_812_814)
