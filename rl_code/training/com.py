import numpy as np
# OpenDSSCOM packages
from win32com.client import makepy
import win32com.client
import sys


class OpenDSSCOM:

    def __init__(self, path):
        self.path = path
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
        self.solve()

        # Variables
        # Note: Inicialization order matters for swithes and lines
        self.switches = self.get_switches()
        self.lines = self.get_lines()
        # --------------------------------------------------------
        self.buses = self.get_buses()
        self.loads = self.get_loads()
        self.num_lines = len(self.lines)
        self.num_switches = len(self.switches)
        self.num_loads = len(self.loads)
        self.start_status = np.asarray([1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1])
        self.switches_init()
        self.solve()

    def com_init(self):
        self.send_command('ClearAll')
        self.DSSText.Command = 'compile ' + self.path
        self.switches_init()
        self.solve()

    def switches_init(self):
        # Switch initialization
        status = np.asarray(self.get_switches_status())
        positions = np.where(self.start_status != status)[0]
        for pos in positions:
            if self.start_status[pos] == 1: self.close_switch(pos)
            else: self.open_switch(pos)
        return self.get_switches_status()

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
        lines = self.DSSLines.AllNames
        switches = []
        for line in lines:
            self.DSSText.Command = f'? Line.{line}.switch'
            boolean = self.DSSText.Result
            if boolean == 'True': switches.append(line)
        return switches

    def get_loads(self):
        return self.DSSLoads.AllNames

    def get_loads_status(self):
        status = []
        self.DSSLoads.First
        for i in range(self.num_loads):
            powers = self.DSSCktElement.Powers.count(0)
            if powers == 4: status.append(0)
            else: status.append(1)
            self.DSSLoads.Next
        return status

    def get_switches_status(self):
        status = []
        for switch in self.switches:
            self.DSSCircuit.SetActiveElement(f'Line.{switch}')
            boolean = self.DSSCktElement.IsOpen(0, 0)
            if boolean == True:
                value = 0
            elif boolean == False:
                value = 1
            status.append(value)
        return status

    def get_num_isolated_loads(self):
        return self.get_loads_status().count(0)

    def get_currents(self):
        num_lines = self.DSSLines.Count
        currents = []
        self.DSSLines.First
        for i in range(num_lines):
            phases = self.DSSLines.Phases
            current = self.DSSCktElement.CurrentsMagAng
            if phases==3:
                currents.append(current[0])
                currents.append(current[2])
                currents.append(current[4])
            if phases==2:
                currents.append(current[0])
                currents.append(current[2])
            if phases ==1:
                currents.append(current[0])
            self.DSSLines.Next
        return currents


    def get_num_loops(self):
        return self.DSSTopology.NumLoops

    def get_ae_conn(self):  # Todo: revisar
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
        self.DSSCircuit.SetActiveElement(f'Line.{self.lines[line]}')
        self.DSSCktElement.Open(0, 0)

    def failure_restoration(self, line):
        self.DSSCircuit.SetActiveElement(f'Line.{self.lines[line]}')
        self.DSSCktElement.Close(0, 0)

    def open_switch(self, switch):
        """Open switch in both terminals
        :param switch: (int)
        """
        self.DSSCircuit.SetActiveElement(f'Line.{self.switches[switch]}')
        self.DSSCktElement.Open(0, 0)

    def close_switch(self, switch):
        """Close switch in both terminals
        :param switch: (int)
        """
        self.DSSCircuit.SetActiveElement(f'Line.{self.switches[switch]}')
        self.DSSCktElement.Close(0, 0)


#com = OpenDSSCOM('E:/pg_fisr/models/IEEE_123_FLISR_Case/Master.dss')
#com.get_currents()