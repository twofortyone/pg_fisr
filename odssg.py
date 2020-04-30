import socket
import numpy as np

class OpenDSSG:

    def __init__(self):
        # Connection data
        self.host = '127.0.0.1'
        self.port = 6345
        self.bz = 20000
        self.s = None

        self.start()

    def start(self):
        # Socket creation
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

    def close(self):
        self.s.close()

    def send(self, msg):
        self.s.sendall(msg)
        recv = self.s.recv(self.bz).decode()[8:-1]
        return recv

    def get_buses(self):
        """Get buses list
        :return: (list)
        """
        buses = self.send(b'42;').split()
        return buses

    def get_lines(self):
        """Get lines list
        :return: (list) """
        lines = self.send(b'33;').split()
        return lines

    def get_voltage_magpu(self):
        """Get voltage mag for all nodes in pu
        :return: (list) voltage mag pu
        """
        voltage = self.send(b'03;').split()
        voltage = [float(x.replace(',', '.')) for x in voltage]
        return voltage

    def send_command(self, command):
        """Send command to OpenDss
        :param command: (str)
        """
        msg = ('25;' + '{0:04X}'.format(len(command)) + f'{command};').encode('UTF-8')
        return self.send(msg)


