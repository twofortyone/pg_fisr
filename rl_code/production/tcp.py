import socket
import numpy as np


class OpenDSSG:

    def __init__(self):
        # Connection data
        self.host = '127.0.0.1'
        self.port = 6345
        self.bz = 8192
        self.s = None
        self.start()

        # Variables
        self.lines = self.get_lines()
        self.buses = self.get_buses()
        self.ss = self.get_switch_status_names()
        self.switches = self.get_switches()
        self.num_lines = len(self.lines)
        self.num_switches = len(self.switches)
        self.start_status = np.asarray(self.get_switches_status())

    def openddsg_init(self):
        status = np.asarray(self.get_switches_status())
        positions = np.where(self.start_status != status)[0]
        for pos in positions:
            self.write_switch_status(pos, self.start_status[pos])
        return self.get_switches_status()

    # -----------------------------------------
    # Getters
    # -----------------------------------------
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

    def get_switches(self):
        return [ss[1] for ss in self.ss]

    def get_switches_status(self):
        return [int(ss[0]) for ss in self.ss]

    def get_voltage_magpu(self):
        """Get voltage mag for all nodes in pu
        :return: (list) voltage mag pu
        """
        voltage = self.send(b'03;')
        return np.asarray([float(x.replace(',', '.')) for x in voltage])

    def get_switch_status_names(self):
        """Get switches status and names
        :return: (list) with tuple of (status int, name str)
        """
        msg = self.send(b'19;')
        return [(int(msg[i]), msg[i + int(len(msg) / 2)]) for i in range(int(len(msg) / 2))]

    # -----------------------------------------
    # Setters
    # -----------------------------------------
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

    def send_command(self, command):
        """Send command to OpenDss
        :param command: (str)
        """
        msg = ('25;' + '{0:04X}'.format(len(command)) + f'{command};').encode('UTF-8')
        return self.send(msg)

    def set_line(self, line):
        msg = ('28;' + '{0:04X}'.format(len(line)) + f'{self.lines[line]};').encode('UTF-8')
        return self.send(msg)

    def write_switch_status(self, switch, status):
        cmd = f'{self.switches[switch]}={status}'
        msg = ('18;' + '{0:04X}'.format(len(cmd)) + f'{cmd};').encode('UTf-8')
        return self.send(msg)

    def fail_line(self, failure):
        cmd = f'open line.{self.lines[failure]} 0 0'
        return self.send_command(cmd)

    def failure_restoration(self, failure):
        cmd = f'close line.{self.lines[failure]} 0 0'
        return self.send_command(cmd)


def decode_message(msg):
    return msg.decode()[8:-1].split()

g = OpenDSSG()