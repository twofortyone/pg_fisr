# Shared packages
import numpy as np

# OpenDssCircuit Packages
from opendss.cominterface import OpenDss


class DistributionSystem:

    def __init__(self):

        self.system = ToPython()
        self.conn = self.system.get_conn()
        self.start_tie_obs = None

        # Variables declaration
        self.nodes_obs = None
        self.nodes_adj_matrix = None
        self.switches_obs = None
        self.closed_switches = None
        self.opened_switches = None
        self.num_nodes = 0
        self.num_switches = 0
        # Method initialization
        self.sys_start()

    def sys_start(self):
        """Update self.system with topython values
        :return: opened_switches (state)
        """
        # Data
        self.start_tie_obs = self.system.get_tie()
        self.nodes_obs = self.system.get_nodes()
        self.num_nodes = len(self.nodes_obs)
        self.nodes_adj_matrix = self.get_adj_matrix()
        self.switches_obs = self.system.get_switches()
        self.num_switches = len(self.switches_obs)

        # Functions
        self.update_switches()
        self.update_node_obs()
        return self.opened_switches

    # --------------------------------
    # NODE's METHODS
    # --------------------------------
    def isolate_nodes(self, switch):
        """Update adjacency matrix when switch connection is modified
        :param switch: (int pos) switch to isolate
        """
        nodes = self.conn[switch]
        pos1 = nodes[0]
        pos2 = nodes[1]
        self.nodes_adj_matrix[pos1, pos2] = 0
        self.nodes_adj_matrix[pos2, pos1] = 0
        # update node obs
        self.update_node_obs()

    def connect_nodes(self, switch):
        """Update adjacency matrix when switch connection is modified
        :param switch: (int pos) switch to connect
        """
        nodes = self.conn[switch]
        pos1 = nodes[0]
        pos2 = nodes[1]
        self.nodes_adj_matrix[pos1, pos2] = 1
        self.nodes_adj_matrix[pos2, pos1] = 1
        # update node obs
        self.update_node_obs()

    def is_node_offline(self, node):
        """Determine if a node is offline
        :param node: (int pos) node to check
        :return: (boolean) True if node is offline
        """
        check = True
        if self.nodes_obs[node] == 1:
            check = False
        return check

    def num_nodes_offline(self):
        """Count number of nodes offline
        :return: number of nodes offline
        """
        return np.count_nonzero(self.nodes_obs == 0)

    def get_adj_matrix(self):
        """ Get the node adjacency matrix (only use at start)
        :return adj: (np array) node adjacency matrix
        """
        adj = np.zeros((self.num_nodes, self.num_nodes))
        for x in self.conn:
            pos1 = x[0]
            pos2 = x[1]
            adj[pos1, pos2] = 1
            adj[pos2, pos1] = 1

        for x in np.nditer(self.start_tie_obs):
            z = self.conn[x]
            pos1 = z[0]
            pos2 = z[1]
            adj[pos1, pos2] = 0
            adj[pos2, pos1] = 0
        return adj

    def update_node_obs(self):
        """Update node_obs after check node adjacency matrix"""
        scn = np.count_nonzero(self.nodes_adj_matrix, axis=0)
        self.nodes_obs = np.where(scn != 0, 1, scn)

    # --------------------------------
    # SWITCH's METHODS
    # --------------------------------
    # Action methods
    def close_switch(self, switch):
        """Close a switch
        :param switch: index of the switch in switches_name
        """
        if self.num_switches > switch >= 0 == self.switches_obs[switch]:
            self.switches_obs[switch] = 1
            # update opened and closed switch list
            self.closed_switches = np.append(self.closed_switches, switch)
            self.opened_switches = np.delete(self.opened_switches, np.where(self.opened_switches == switch))
            # update nodes connection
            self.connect_nodes(switch)

    def open_switch(self, switch):
        """Open a switch and update closed and opened switches and node adjacency matrix
        :param switch: index of the switch in switches_name
        """
        if 0 <= switch < self.num_switches and self.switches_obs[switch] == 1:
            self.switches_obs[switch] = 0
            # update opened and closed switch array
            self.closed_switches = np.delete(self.closed_switches, np.where(self.closed_switches == switch))
            self.opened_switches = np.append(self.opened_switches, switch)

            # update node connections
            self.isolate_nodes(switch)

    def update_switches(self):
        """ Get closed and opened switches from switches obs (only use at start)"""
        self.closed_switches = np.where(self.switches_obs == 1)[0]
        self.opened_switches = np.where(self.switches_obs == 0)[0]

    # --------------------------------
    # FAILURE's METHODS
    # --------------------------------
    def do_failure(self, line):
        self.open_switch(line)


class ToPython:

    def __init__(self):
        open_dss = OpenDssCircuit()
        self.nodes = open_dss.nodes
        self.switches = open_dss.lines
        self.tie = open_dss.ties
        self.conn = open_dss.get_conn()

    def get_conn(self):
        """ Connection list 
        :returns conn: (list) node tuple connection list  
        """
        conn = []
        for x in self.conn:
            pos = []
            for z in x:
                pos.append(find_pos(self.nodes, z))
            conn.append(tuple(pos))
        return conn

    def get_tie(self):
        tie = []
        for x in self.tie:
            pos = find_pos(self.switches, x)
            tie.append(pos)
        return np.asarray(tie)

    def get_switches(self):
        """Switches list 
        :returns switches: (numpy array int) 0 for open and 1 for close switch
        """
        switches = np.ones(len(self.switches))
        tie = self.get_tie()
        for x in tie:
            switches[x] = 0
        return switches.astype(int)

    def get_nodes(self):
        """ Node list 
        :returns nodes: (numpy array int) zeros array
        """
        # TODO: update nodes values certainly
        nodes = np.zeros(len(self.nodes))
        return nodes.astype(int)

    def get_switch_pos(self, name):
        return find_pos(self.switches, name)

    def get_node_pos(self, node):
        return find_pos(self.nodes, node)

    def get_switches_names(self, positions):
        """Find the switch names
        :param positions: list with switch positions
        :return names: list with switch names
        """
        names = []
        for i in positions:
            names.append(self.switches[i])
        return names

    def get_nodes_names(self, positions):
        """Find the node names
        :param positions: list with node positions
        :return names: list with node names
        """
        names = []
        for i in positions:
            names.append(self.nodes[i])
        return names


class OpenDssCircuit:

    def __init__(self):
        path = 'D:\Bus_37\ieee37.dss'
        self.com = OpenDss(path)
        self.com.solve()

        self.lines = self.com.get_lines()
        self.nodes = self.com.get_buses()
        self.ties = self.lines[10:30]

    def get_conn(self):
        """Get line connection scheme between nodes
        :return conn: (np array) line connections
        """
        conn = []
        for x in self.lines:
            self.set_active_line(x)
            nodes = self.get_conn_element()
            aux = []
            for y in nodes:
                aux.append(y.split('.')[0])
            conn.append(aux)
        return conn

    def set_active_line(self, line):
        """Set line param as active element
        :param line: (str) line name
        """
        line = 'Line.' + line
        self.com.set_active_element(line)

    def get_conn_element(self):
        """Get node connection by active element
        :return: (tuple) element connection
        """
        return self.com.get_ae_busnames()


# Methods to used across
def find_pos(elements, element): return elements.index(element)


def fin_element(elements, pos): return elements[pos]
