import numpy as np
# OpenDSSCOM packages
from win32com.client import makepy
import win32com.client
import sys


class OpenDSSCOM:

    def __init__(self, path):
        # --------------------------------------------------------------------------------------------------------------
        # COM Interface
        # --------------------------------------------------------------------------------------------------------------
        self.path = path
        sys.argv = ["makepy", "OpenDSSEngine.DSS"]
        makepy.main()
        self.DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
        self.DSSText = self.DSSObj.Text  # Returns the DSS command result
        self.DSSCircuit = self.DSSObj.ActiveCircuit # Returns interface to the active circuit
        self.DSSSolution = self.DSSCircuit.Solution # Return an interface to the solution object
        self.DSSLines = self.DSSCircuit.Lines  # Return interface to lines collection
        self.DSSLoads = self.DSSCircuit.Loads  # Return interface to loads collection
        self.DSSBus = self.DSSCircuit.ActiveBus  # Return the interface to the active bus
        self.DSSCktElement = self.DSSCircuit.ActiveCktElement # Return interface to active element
        self.DSSStart = self.DSSObj.Start(0)
        self.DSSTopology = self.DSSCircuit.Topology
        self.DSSMeter = self.DSSCircuit.Meters
        if self.DSSStart:
            print("OpenDSS Engine started successfully")
        else:
            print("Unable to start the OpenDSS Engine")
        self.DSSText.Command = 'compile ' + self.path
        self.solve()
        # --------------------------------------------------------------------------------------------------------------
        # Distribution Network Variables
        # --------------------------------------------------------------------------------------------------------------
        # Note: Inicialization order matters for swithes and lines
        self.switches = self.get_switches()
        self.lines = self.get_lines()
        self.buses = self.get_buses()
        self.loads = self.get_loads()
        self.num_switches = len(self.switches)
        self.num_lines = len(self.lines)
        self.num_buses = len(self.buses)
        self.num_loads = len(self.loads)
        #self.default_status = np.asarray([1,1,1,1,1])
        #self.start_status = np.asarray([0,0,0,0,0]) # start tie para 33 bus
        #self.default_status = np.asarray([1,1,1,1,1,1,1,1,1,1])
        #self.start_status = np.asarray([1,1,1,1,0,1,0,1,0,1])  # start tie para 123 bus
        self.default_status = self.get_switches_status()
        self.start_status = self.get_switches_status()
        #self.switches_init()
        #self.solve()
        # --------------------------------------------------------------------------------------------------------------
        # Distribution Network Representation
        # --------------------------------------------------------------------------------------------------------------
        self.lines_con = self.get_conn()
        self.buses_obs = np.zeros(self.num_buses).astype(int)
        self.adj_matrix = self.get_adj_matrix()
        self.update_node_obs() # Call after adj_matrix()
        self.inc_matrix = None
        self.time_step = 0


    def com_init(self):
        self.send_command('ClearAll')
        self.DSSText.Command = 'compile ' + self.path
        self.switches_init()
        self.solve()

    def clear_run(self):
        self.send_command('ClearAll')
        self.DSSText.Command = 'compile ' + self.path

    def topology(self):
        return self.DSSTopology.NumLoops

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

    # DN Representation
    def get_conn(self):
        """Get line connection scheme between buses (pos)
        :return conn: (tuple 2d) line connections
        """
        conn = []
        for line in self.DSSLines.AllNames:
            self.DSSCircuit.SetActiveElement(f'Line.{line}')
            buses = self.DSSCktElement.BusNames
            aux = []
            for bus in buses:
                aux.append(self.buses.index(bus.split('.')[0]))
            conn.append(tuple(aux))
        return tuple(conn)

    def get_adj_matrix(self):
        adj = np.zeros((self.num_buses, self.num_buses))
        for connection in self.lines_con:
            pos1 = connection[0]
            pos2 = connection[1]
            adj[pos1, pos2] = 1
            adj[pos2, pos1] = 1

        ss = self.get_switches_status()
        ss_pos = np.where(np.asarray(ss)==0)[0]
        for switch_pos in ss_pos:
            sw_con = self.lines_con[self.num_lines+int(switch_pos)]
            pos1 = sw_con[0]
            pos2 = sw_con[1]
            adj[pos1, pos2] = 0
            adj[pos2, pos1] = 0
        return adj

    def update_node_obs(self):
        """Update node_obs after check node adjacency matrix"""
        scn = np.count_nonzero(self.adj_matrix, axis=0)
        self.buses_obs = np.where(scn != 0, 1, scn)

    # DN Variables
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
            if powers >= 4: status.append(0)
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
        self.send_command(f'New EnergyMeter.EM{self.time_step} Element = Line.{self.lines[0]} Terminal=1')
        self.solve()
        self.time_step += 1
        return self.DSSTopology.NumLoops

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


#com = OpenDSSCOM('E:\pg_fisr\models\IEEE_13_Bus-G\Master.dss')
#com = OpenDSSCOM('E:\IEEE_8500_Bus-G/Master.DSS')
com = OpenDSSCOM('E:/pg_fisr/data/models/IEEE_123_FLISR_Case/Master.DSS')