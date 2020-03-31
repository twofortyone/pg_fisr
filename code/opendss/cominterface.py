import win32com.client
from win32com.client import makepy
import sys


class OpenDss:

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

    def get_path(self):
        return self.path

    def get_version(self):
        return self.DSSObj.Version

    def get_voltages(self):
        return self.DSSBus.VMagAngle

    def get_buses(self):
        """Get buses list
        :return: (tuple)
        """
        return self.DSSCircuit.AllBusNames

    def get_active_element(self):
        return self.DSSCktElement.Name

    def get_bus_vmagpu(self):
        return self.DSSCircuit.AllBusVmagPu

    def get_bus_vmag(self):
        return self.DSSCircuit.AllBusVmag

    def get_lines(self):
        """Get lines list
        :return: (tuple) """
        return self.DSSLines.AllNames

    def get_loads(self):
        return self.DSSLoads.AllNames

    def get_ae_conn(self):
        """Active element nodes connection
        :return: (tuple)
        """
        return self.DSSCktElement.BusNames

    def get_ae_data(self):
        currents = self.DSSCktElement.CurrentsMagAng
        voltages = self.DSSCktElement.Voltages
        enabled = self.DSSCktElement.Enabled
        return currents, voltages, enabled

    def get_ae_currents(self):
        return self.DSSCktElement.CurrentsMagAng

    # Verify if the active element is open given the terminal
    def ae_is_open(self, term):
        return self.DSSCktElement.IsOpen(term, 1)

    def send_command(self, command):
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






