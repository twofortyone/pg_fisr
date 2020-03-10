import win32com.client
from win32com.client import makepy
import sys


class Opendss:

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
        self.DSSBus = self.DSSCircuit.ActiveBus  # Return the interface to the active bus
        self.DSSCtrlQueue = self.DSSCircuit.CtrlQueue  # Interface to the main control queue
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

    def send_command(self, command):
        self.DSSText.Command = command

    def solve(self):
        self.DSSSolution.Solve()

    def get_voltages(self):
        return self.DSSBus.VMagAngle

    # voltajes = DSSBus.VMagAngle
    # nombre = DSSBus.Name
    # print(nombre, voltajes)
    # print(DSSCircuit.AllBusVmag)
