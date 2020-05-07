import socket
import numpy as np


class OpenDSSG:

    def __init__(self):
        # Connection data
        self.host = '127.0.0.1'
        self.port = 6345
        self.bz = 100000
        self.s = None

        self.start()


    def start(self):
        # Socket creation
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

    def close(self):
        self.s.close()

    def send(self, msg):
        try:
            self.s.sendall(msg)
            recv = decode_message(self.s.recv(self.bz))
        except ConnectionAbortedError:
            self.start()
            self.s.sendall(msg)
            recv = decode_message(self.s.recv(self.bz))
        return recv

    def get_buses(self):
        """Get buses list
        :return: (list)
        """
        buses = self.send(b'42;')
        return buses

    def get_lines(self):
        """Get lines list
        :return: (list) """
        lines = self.send(b'33;')
        return lines

    def get_voltage_magpu(self):
        """Get voltage mag for all nodes in pu
        :return: (list) voltage mag pu
        """
        voltage = self.send(b'03;')
        return np.asarray([float(x.replace(',', '.')) for x in voltage])

    def send_command(self, command):
        """Send command to OpenDss
        :param command: (str)
        """
        msg = ('25;' + '{0:04X}'.format(len(command)) + f'{command};').encode('UTF-8')
        return self.send(msg)

    def get_switch_status_names(self):
        """Get switches status and names
        :return: (list) with tuple of (status int, name str)
        """
        msg = self.send(b'19;')
        return [(int(msg[i]), msg[i + int(len(msg) / 2)]) for i in range(int(len(msg) / 2))]

    def set_line(self, line):
        msg = ('28;' + '{0:04X}'.format(len(line)) + f'{line};').encode('UTF-8')
        return self.send(msg)

    def write_switch_status(self,switch, status):
        cmd = f'{switch}={status}'
        msg = ('18;' + '{0:04X}'.format(len(cmd)) + f'{cmd};').encode('UTf-8')
        return self.send(msg)



def decode_message(msg):
    return msg.decode()[8:-1].split()


g = OpenDSSG()

# lm = list(product(l, repeat = 12))