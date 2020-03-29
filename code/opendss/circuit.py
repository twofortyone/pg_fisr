from opendss.cominterface import OpenDss
import numpy as np


class Circuit:

    def __init__(self, path):
        # COM object initialization
        self.com = OpenDss(path)
        self.com.solve()

        self.voltages_pu = np.asarray(self.com.get_bus_vmagpu())
        self.lines = np.asarray(self.com.get_lines())
        self.buses = np.asarray(self.com.get_buses())
        self.loads = np.asarray(self.com.get_loads())

    def update(self):
        self.voltages_pu = np.asarray(self.com.get_bus_vmagpu())
        self.lines = np.asarray(self.com.get_lines())
        self.buses = np.asarray(self.com.get_buses())

    def check_voltages_limits(self):
        check = False
        for i in self.voltages_pu:
            if (0.90 > i > 0.1) or i > 1.05:
                check = True
                break
        return check, i

    def open_switch(self, line, term):
        self.set_active_line(line)
        self.com.open_element(term)
        self.com.solve()
        self.update()

    def close_switch(self, line, term):
        self.set_active_line(line)
        self.com.close_element(term)
        self.com.solve()
        self.update()

    def set_active_load(self, load):
        load = 'Load.' + load
        self.com.set_active_element(load)

    # used OpenDssCircuit class
    def set_active_line(self, line):
        line = 'Line.' + line
        self.com.set_active_element(line)

    def is_line_open(self, line, term):
        self.set_active_line(line)
        line = self.get_ae_name()
        status = self.com.ae_is_open(term)
        return line, status

    def num_load_offline(self):
        count = 0
        for i in self.loads:
            self.set_active_load(i)
            current = self.get_ae_currents()[0]
            if current <= 0.5:
                count += 1
        return count

    def get_buses(self):
        return self.buses

    def get_lines(self):
        return self.lines

    def get_voltages_pu(self):
        return self.voltages_pu

    def get_loads(self):
        return self.loads

    def get_ae_name(self):
        return self.com.get_active_element()

    #rename get_conn_element
    def get_ae_buses(self):
        return self.com.get_ae_busnames()

    def get_ae_currents(self):
        return self.com.get_ae_currents()

    def get_ae_data(self):
        return self.com.get_ae_data()

    def get_loadsbuses(self):
        load_buses = []
        for i in self.loads:
            self.set_active_load(i)
            buses = self.get_ae_buses()
            load_buses.append([i, buses[0]])
        return load_buses

