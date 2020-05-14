import numpy as np
# OpenDSSCOM packages
from win32com.client import makepy
import win32com.client
import sys


class OpenDSSCOM:

    def __init__(self):
        self.path = 'E:\opfi\IEEE_123_FLISR_Case\Master.dss'
        sys.argv = ["makepy", "OpenDSSEngine.DSS"]
        makepy.main()
        self.DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
        self.DSSText = self.DSSObj.Text  # Returns the DSS command result
        # Returns interface to the active circuit
        self.DSSCircuit = self.DSSObj.ActiveCircuit
        # Return an interface to the solution object
        self.DSSSolution = self.DSSCircuit.Solution
        # self.DSSParallel = self.DSSCircuit.Parallel  # Delivers a handler for the parallel dispatch interface
        self.DSSLines = self.DSSCircuit.Lines  # Return interface to lines collection
        self.DSSLoads = self.DSSCircuit.Loads  # Return interface to loads collection
        # Return the interface to the active bus
        self.DSSBus = self.DSSCircuit.ActiveBus
        # self.DSSCtrlQueue = self.DSSCircuit.CtrlQueue  # Interface to the main control queue
        # Return interface to active element
        self.DSSCktElement = self.DSSCircuit.ActiveCktElement
        self.DSSStart = self.DSSObj.Start(0)
        self.DSSReclosers = self.DSSCircuit.Reclosers
        self.DSSTopology = self.DSSCircuit.Topology
        if self.DSSStart:
            print("OpenDSS Engine started successfully")
        else:
            print("Unable to start the OpenDSS Engine")
        self.DSSText.Command = 'compile ' + self.path

        # Variables
        self.lines = self.get_lines()
        self.buses = self.get_buses()
        self.switches = self.get_switches()
        self.num_lines = len(self.lines)
        self.num_switches = len(self.switches)

    def com_init(self):
        self.send_command('ClearAll')
        self.DSSText.Command = 'compile ' + self.path

    # -----------------------------------------
    # Getters
    # -----------------------------------------
    def get_lines(self):
        """Get lines list
        :return: (list) """
        switches = self.get_switches()
        lines = list(self.DSSLines.AllNames)
        for switch in switches:
            lines.remove(switch)
        return lines

    def get_buses(self):
        """Get buses list
        :return: (tuple)
        """
        return self.DSSCircuit.AllBusNames

    def get_switches(self):
        return self.DSSReclosers.AllNames

    def get_switches_status(self):
        self.DSSReclosers.First
        status = []
        for i in range(self.num_switches):
            boolean = self.DSSCktElement.IsOpen(0, 0)
            if boolean == True:
                value = 0
            elif boolean == False:
                value = 1
            status.append(value)
            self.DSSReclosers.Next
        return status

    def get_num_isolated_loads(self):
        return self.DSSTopology.NumIsolatedLoads

    def get_num_loops(self):
        return self.DSSTopology.NumLoops

    # Todo: revisar
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
        return np.asarray(self.DSSCircuit.AllBusVmagPu)

    def get_active_element(self):
        """Get active element name
        :return: name
        """
        return self.DSSCktElement.Name

    def show_voltages(self):
        """Show voltages as txt """
        self.send_command('show voltages LN nodes')

    def show_currents(self):
        """Show currents as txt"""
        self.send_command('show currents elements')

    def ae_is_open(self):
        """Verify is active element is opened
        :return: [boolean, boolean]"""
        term1 = self.DSSCktElement.IsOpen(1, 0)
        term2 = self.DSSCktElement.IsOpen(2, 0)
        return [term1, term2]

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

    def fail_line(self, line):
        self.DSSCircuit.SetActiveElement(f'Line.{line}')
        self.DSSCktElement.Open(0, 0)

    def failure_restoration(self, line):
        self.DSSCircuit.SetActiveElement(f'Line.{line}')
        self.DSSCktElement.Close(0, 0)

    def open_switch(self, switch):
        """Open switch in both terminals
        :param line: (name str)
        """
        self.DSSCircuit.SetActiveElement(f'Line.{switch}')
        self.DSSCktElement.Open(0, 0)

    def close_switch(self, switch):
        """Close switch in both terminals
        :param line: (name str)
        """
        self.DSSCircuit.SetActiveElement(f'Line.{switch}')
        self.DSSCktElement.Close(0, 0)


opendss = OpenDSSCOM()

# Todo: borrar 
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

#opendss = OpenDSSCOM('E:\opfi\IEEE_123_FLISR_Case\Hola.dss')