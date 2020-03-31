# OpenDSSCOM packages
from win32com.client import makepy
import win32com.client
import sys


class OpenDSSCircuit:

    def __init__(self):
        path = 'E:\ieee33bus.dss'
        self.com = OpenDSSCOM(path)
        self.com.solve()

        self.lines = self.com.get_lines()
        self.nodes = self.com.get_buses()
        self.ties = self.lines[32:37]

        for x in self.ties:
            self.open_switch(x)

    # ----------------------------------------
    # Getters
    # -----------------------------------------
    def get_lines(self):
        """Get lines name list
        :return: (tuple) lines name list
        """
        return self.lines

    def get_nodes(self):
        """Get nodes name list
        :return: (tuple) nodes name list
        """
        return self.nodes

    def get_ties(self):
        """Get ties switches name list
        :return: (tuple) ties switches name list
        """
        return self.ties

    def get_conn(self):
        """Get line connection scheme between nodes
        :return conn: (tuple 2d) line connections
        """
        conn = []
        for x in self.lines:
            self.set_active_line(x)
            nodes = self.get_conn_element()
            aux = []
            for y in nodes:
                aux.append(y.split('.')[0])
            conn.append(tuple(aux))
        return tuple(conn)

    def get_conn_element(self):
        """Get node connection by active element
        :return: (tuple) element connection
        """
        return self.com.get_ae_conn()

    def get_voltage(self):
        """Get node voltages magnitude in pu
        :return:  (np array) node voltages
        """
        v = self.com.get_voltage_magpu()
        vn = np.asarray(v).reshape((-1, 3))
        return vn

    # ----------------------------------------
    # Setters
    # -----------------------------------------
    def set_active_line(self, line):
        """Set line param as active element
        :param line: (str) line name
        """
        line = 'Line.' + line
        self.com.set_active_element(line)

    def open_switch(self, line):
        """Open switch in both terminals
        :param line: (name str)
        """
        self.set_active_line(line)
        self.com.open_element(1)
        self.com.open_element(2)
        self.com.solve()
        # TODO: update voltage values

    def close_switch(self, line):
        """Close switch in both terminals
        :param line: (name str)
        """
        self.set_active_line(line)
        self.com.close_element(1)
        self.com.close_element(2)
        self.com.solve()
        # TODO: update voltage values


class OpenDSSCOM:

    def __init__(self, path):
        self.path = path
        sys.argv = ["makepy", "OpenDSSEngine.DSS"]
        makepy.main()
        self.DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
        self.DSSText = self.DSSObj.Text  # Returns the DSS command result
        self.DSSCircuit = self.DSSObj.ActiveCircuit  # Returns interface to the active circuit
        self.DSSSolution = self.DSSCircuit.Solution  # Return an interface to the solution object
        self.DSSParallel = self.DSSCircuit.Parallel  # Delivers a handler for the parallel dispatch interface
        self.DSSLines = self.DSSCircuit.Lines  # Return interface to lines collection
        self.DSSLoads = self.DSSCircuit.Loads  # Return interface to loads collection
        self.DSSBus = self.DSSCircuit.ActiveBus  # Return the interface to the active bus
        self.DSSCtrlQueue = self.DSSCircuit.CtrlQueue  # Interface to the main control queue
        self.DSSCktElement = self.DSSCircuit.ActiveCktElement  # Return interface to active element
        self.DSSStart = self.DSSObj.Start(0)
        if self.DSSStart:
            print("OpenDSS Engine started successfully")
        else:
            print("Unable to start the OpenDSS Engine")

        self.DSSText.Command = 'compile ' + self.path

    # -----------------------------------------
    # Getters
    # -----------------------------------------
    def get_lines(self):
        """Get lines list
        :return: (tuple) """
        return self.DSSLines.AllNames

    def get_buses(self):
        """Get buses list
        :return: (tuple)
        """
        return self.DSSCircuit.AllBusNames

    def get_ae_conn(self):
        """Active element nodes connection
        :return: (tuple)
        """
        return self.DSSCktElement.BusNames

    def get_ae_current(self):
        """Get active element current
        :return: (tuple)
        """
        return self.DSSCktElement.CurrentsMagAng

    def get_voltage_magpu(self):
        """Get voltage mag for all nodes in pu
        :return: (tuple) voltage mag pu
        """
        return self.DSSCircuit.AllBusVmagPu

    # -----------------------------------------
    # Setters
    # -----------------------------------------
    def send_command(self, command):
        """Send command to OpenDss
        :param command: (str)
        """
        self.DSSText.Command = command

    def solve(self):
        """Solve the OpenDSS model """
        self.DSSSolution.Solve()

    def set_active_element(self, element):
        """Set element as active
        :param element: (str) name
        """
        self.DSSCircuit.SetActiveElement(element)

    def open_element(self, term):
        """Open active element
        :param term: (int) terminal (1 or 2)
        """
        self.DSSCktElement.Open(term, 0)

    def close_element(self, term):
        """Close active element
        :param term: (int) terminal (1 or 2)
        """
        self.DSSCktElement.Close(term, 0)

    def show_voltages(self):
        """Show voltages as txt """
        self.send_command('show voltages LN nodes')

    def show_currents(self):
        """Show currents as txt"""
        self.send_command('show currents elements')
