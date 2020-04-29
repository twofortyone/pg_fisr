# Shared packages
import numpy as np

# DistributionSystem packages
import pandas as pd
from scipy.sparse import csgraph

# OpenDSS2Python packages
from rl_code.opendss import OpenDSSCircuit


class DistributionSystem:

    def __init__(self, opendss_path, ties, vol_ftr):
        self.system_data = OpenDSS2Python(opendss_path, ties)
        self.conn = self.system_data.get_conn()  # list
        self.start_tie_obs = []  # list

        # Variables declaration
        self.nodes_obs = None
        self.inc_matrix = None 
        self.switches_obs = None
        self.closed_switches = None
        self.opened_switches = None
        self.num_nodes = self.system_data.open_dss.num_nodes
        self.num_switches = self.system_data.open_dss.num_switches 
        voltages = pd.read_feather(vol_ftr)
        self.voltages = voltages.to_numpy()
        # Method initialization
        self.sys_start()

    def sys_start(self):
        """Update self.system with OpenDSS2Python values
        :return: opened_switches (state)
        """
        # Data
        self.start_tie_obs = self.system_data.get_tie()
        self.switches_obs = self.system_data.get_switches()
        self.inc_matrix = self.get_inc_matrix()
        self.nodes_adj_matrix = self.get_adj_matrix()
        
        # Functions
        self.update_node_obs()
        self.update_switches()
        return self.opened_switches

    # --------------------------------
    # GETTERS METHODS
    # --------------------------------
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

        for x in self.start_tie_obs:
            z = self.conn[x]
            pos1 = z[0]
            pos2 = z[1]
            adj[pos1, pos2] = 0
            adj[pos2, pos1] = 0
        return adj

    def get_voltage(self, state):
        voltages = self.voltages[:, state]
        return voltages

    def nodes_isolated(self):
        l = csgraph.laplacian(self.nodes_adj_matrix, normed=False)
        e = np.around(np.linalg.eigvals(l), 5)
        return np.count_nonzero(e == 0)

    def nodes_loop(self):
        return np.count_nonzero(self.nodes_obs >1)
    
    def get_inc_matrix(self):
        m = np.zeros((self.num_nodes, self.num_switches))

        i = 0 
        for x in self.conn: 
            pos1 = x[0]
            pos2 = x[1]
            m[pos1, i] = -1
            m[pos2, i] = 1 
            i += 1

        for x in self.start_tie_obs: 
            z = self.conn[x]
            pos1 = z[0]
            pos2 = z[1]
            m[pos1, x]= 0
            m[pos2, x]= 0
        return m 

    # --------------------------------
    # SETTERS METHODS
    # --------------------------------
    def inc_exploration(self, node_init):
        for x in node_init:
            vertex = self.inc_matrix[:, x]
            node_trans = np.where(vertex == 1)[0]
            self.nodes_obs[node_trans[0]]+=1
            nodo = self.inc_matrix[node_trans[0], :]
            ver_trans = np.where(nodo == -1)[0]
            if ver_trans.shape[0]>0:
                self.inc_exploration(ver_trans)    

    def isolate_nodes(self, switch):
        """Update adjacency matrix when switch connection is modified
        :param switch: (int pos) switch to isolate
        """
        nodes = self.conn[switch]
        pos1 = nodes[0]
        pos2 = nodes[1]
        # update inc matrix 
        self.inc_matrix[pos1, switch]= 0
        self.inc_matrix[pos2, switch]= 0
        # update adj
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
        # update inc matrix 
        self.inc_matrix[pos1, switch]= -1
        self.inc_matrix[pos2, switch]= 1
        # update adj
        self.nodes_adj_matrix[pos1, pos2] = 1
        self.nodes_adj_matrix[pos2, pos1] = 1
        # update node obs
        self.update_node_obs()

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

    def update_node_obs(self):
        """Update node_obs after check node adjacency matrix"""
        self.nodes_obs = self.system_data.get_nodes()
        self.nodes_obs[0]=1
        node_init = np.where(self.inc_matrix[0,:]==-1)[0]
        self.inc_exploration(node_init)


class OpenDSS2Python:

    def __init__(self, opendss_path, ties):
        self.open_dss = OpenDSSCircuit(opendss_path, ties)
        self.nodes = self.open_dss.get_nodes()
        self.switches = self.open_dss.get_lines()
        self.tie = self.open_dss.get_ties()
        self.conn = self.open_dss.get_conn()

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

    def get_tie(self):
        """Get tie switches
        :return tie: (list) positions for tie in switches
        """
        tie = []
        for x in self.tie:
            pos = find_pos(self.switches, x)
            tie.append(pos)
        return tie

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

    # ---------------------------------------
    # Get position methods
    # ---------------------------------------
    def get_switch_pos(self, name):
        """Get switch position from switch name
        :param name: switch name
        :return: (int) switch position
        """
        return find_pos(self.switches, name)

    def get_node_pos(self, node):
        """Get node position from node name
        :param node: node name
        :return: (int) node position
        """
        return find_pos(self.nodes, node)

    # ---------------------------------------
    # Get name methods
    # ---------------------------------------
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
        :return names: (list) list with node names
        """
        names = []
        for i in positions:
            names.append(self.nodes[i])
        return names


# Methods to used across
def find_pos(elements, element): return elements.index(element)


def fin_element(elements, pos): return elements[pos]
