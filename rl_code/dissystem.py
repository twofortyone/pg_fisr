# Shared packages
import numpy as np

# DistributionSystem packages
import pandas as pd
from scipy.sparse import csgraph
from odssg import OpenDSSG


class DistributionSystem:

    def __init__(self):
        self.opendssg = OpenDSSG()

        # Variables declaration
        self.num_nodes = len(self.opendssg.get_buses())
        self.num_switches = len(self.opendssg.get_switch_status_names())
        self.num_lines = len(self.opendssg.get_lines())
        self.switches_obs = np.asarray(self.get_switches_status())
        self.switches = self.get_switches()
        self.lines = self.opendssg.get_lines()

        self.nodes_obs = np.zeros(len(self.opendssg.get_buses())) # Todo revisar uso
        self.inc_matrix = None
        self.nodes_adj_matrix = None
        #self.closed_switches = None
        #self.opened_switches = None
        # Method initialization
        #self.conn = self.system_data.get_conn()  # list todo cambiar por incidencia mtrix
        #self.sys_start()

    def sys_start(self):
        """Update self.system with OpenDSS2Python values
        :return: opened_switches (state)
        """
        self.inc_matrix = self.get_inc_matrix()
        self.nodes_adj_matrix = self.get_adj_matrix()
        
        # Functions
        self.update_node_obs()
        return self.opened_switches

    # --------------------------------
    # GETTERS METHODS
    # --------------------------------
    def get_voltage(self):  # checked
        return np.asarray(self.opendssg.get_voltage_magpu())

    def get_switches(self):  # checked
        sws = self.opendssg.get_switch_status_names()
        return [x[1] for x in sws]

    def get_switches_status(self):  # checked
        sws = self.opendssg.get_switch_status_names()
        return [int(x[0]) for x in sws]

    def get_adj_matrix(self): # todo borrar
        """ Get the node adjacency matrix (only use at start)
        :return adj: (np array) node adjacency matrix
        """
        adj = np.zeros((self.num_nodes, self.num_nodes))
        for x in self.conn:
            pos1 = x[0]
            pos2 = x[1]
            adj[pos1, pos2] = 1
            adj[pos2, pos1] = 1
        return adj

    def nodes_isolated(self):
        l = csgraph.laplacian(self.nodes_adj_matrix, normed=False)
        e = np.around(np.linalg.eigvals(l), 5)
        return np.count_nonzero(e == 0)

    def nodes_loop(self):
        return np.count_nonzero(self.nodes_obs > 1)
    
    def get_inc_matrix(self): # todo borrar
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
            m[pos1, x] = 0
            m[pos2, x] = 0
        return m 

    # --------------------------------
    # SETTERS METHODS
    # --------------------------------

    def operate_switch(self, switch, action):  # checked
        self.opendssg.write_switch_status(self.switches[switch], action)

    def failure_line(self, failure):
        cmd = f'open line.{self.lines[failure]} 0 0'
        return self.opendssg.send_command(cmd)

    def fix_failure(self, failure):
        cmd = f'close line.{self.lines[failure]} 0 0'
        return self.opendssg.send_command(cmd)


    def inc_exploration(self, node_init):
        for x in node_init:
            vertex = self.inc_matrix[:, x]
            node_trans = np.where(vertex == 1)[0]
            self.nodes_obs[node_trans[0]] += 1
            nodo = self.inc_matrix[node_trans[0], :]
            ver_trans = np.where(nodo == -1)[0]
            if ver_trans.shape[0] > 0:
                self.inc_exploration(ver_trans)    

    def isolate_nodes(self, switch):
        """Update adjacency matrix when switch connection is modified
        :param switch: (int pos) switch to isolate
        """
        nodes = self.conn[switch]
        pos1 = nodes[0]
        pos2 = nodes[1]
        # update inc matrix 
        self.inc_matrix[pos1, switch] = 0
        self.inc_matrix[pos2, switch] = 0
        # update adj
        self.nodes_adj_matrix[pos1, pos2] = 0
        self.nodes_adj_matrix[pos2, pos1] = 0
        # update node obs
        # Todo restaurar: self.update_node_obs()

    def connect_nodes(self, switch):
        """Update adjacency matrix when switch connection is modified
        :param switch: (int pos) switch to connect
        """
        nodes = self.conn[switch]
        pos1 = nodes[0]
        pos2 = nodes[1]
        # update inc matrix 
        self.inc_matrix[pos1, switch] = -1
        self.inc_matrix[pos2, switch] = 1
        # update adj
        self.nodes_adj_matrix[pos1, pos2] = 1
        self.nodes_adj_matrix[pos2, pos1] = 1
        # update node obs
        # Todo restarurar: self.update_node_obs()

    def close_switch(self, switch):
        """Close a switch
        :param switch: index of the switch in switches_name
        """
        if self.num_switches > switch >= 0 == self.switches_obs[switch]:
            # update nodes connection
            self.connect_nodes(switch)
            # open opendss-g
            self.opendssg.write_switch_status(switch, 1)

    def open_switch(self, switch):
        """Open a switch and update closed and opened switches and node adjacency matrix
        :param switch: index of the switch in switches_name
        """
        if 0 <= switch < self.num_switches and self.switches_obs[switch] == 1:
            # update node connections
            self.isolate_nodes(switch)
            # open opendss-g
            self.opendssg.write_switch_status(switch, 0)

    def update_node_obs(self):
        """Update node_obs after check node adjacency matrix"""
        self.nodes_obs = self.system_data.get_nodes()
        self.nodes_obs[0] = 1
        node_init = np.where(self.inc_matrix[0, :] == -1)[0]
        self.inc_exploration(node_init)
