import numpy as np


class DistributionSystem:

    def __init__(self, system):

        self.sd = system
        self.conn = self.sd.get_conn()
        self.start_tie_obs = self.sd.get_tie()
        # Variables declaration
        self.nodes_obs = self.sd.get_nodes()
        self.nodes_adj_matrix = self.get_adj_matrix()
        self.switches_obs = self.sd.get_switches()
        self.closed_switches = []
        self.opened_switches = []
        # Method initialization
        self.sys_start()

    def sys_start(self):
        self.update_switches()
        self.update_node_obs()

    # --------------------------------
    # NODE's METHODS
    # --------------------------------
    def isolate_nodes(self, switch):
        nodes = self.conn[switch]
        pos1 = nodes[0]
        pos2 = nodes[1]
        self.nodes_adj_matrix[pos1, pos2] = 0
        self.nodes_adj_matrix[pos2, pos1] = 0
        # update node obs
        self.update_node_obs()

    def connect_nodes(self, switch):
        nodes = self.conn[switch]
        pos1 = nodes[0]
        pos2 = nodes[1]
        self.nodes_adj_matrix[pos1, pos2] = 1
        self.nodes_adj_matrix[pos2, pos1] = 1
        # update node obs
        self.update_node_obs()

    def is_node_offline(self, node):
        check = True
        if self.nodes_obs[node] == 1:
            check = False
        return check

    def num_nodes_offline(self):
        return self.nodes_obs.count(0)

    def get_adj_matrix(self):
        nm = len(self.nodes_obs)
        adj = np.zeros((nm, nm))
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

    def update_node_obs(self):
        for x in range(len(self.nodes_obs)):
            self.nodes_obs[x] = 0
        for i in range(len(self.nodes_obs)):
            for j in range(len(self.nodes_obs)):
                if self.nodes_adj_matrix[i, j] == 1:
                    self.nodes_obs[i] = 1
                    break

    # --------------------------------
    # SWITCH's METHODS
    # --------------------------------
    # Action methods
    def close_switch(self, switch):
        """Close a switch
        :param switch: index of the switch in switches_name
        """
        obs = self.switches_obs
        if 0 <= switch < len(obs) and obs[switch] == 0:
            obs[switch] = 1
            # update opened and closed switch list
            self.closed_switches.append(switch)
            self.opened_switches.remove(switch)
            # update nodes connection
            self.connect_nodes(switch)

    def open_switch(self, switch):
        """Open a switch
        :param switch: index of the switch in switches_name
        """
        obs = self.switches_obs
        if 0 <= switch < len(obs) and obs[switch] == 1:
            obs[switch] = 0
            # update opened and closed switch list
            self.closed_switches.remove(switch)
            self.opened_switches.append(switch)
            # update node connections
            self.isolate_nodes(switch)

    def update_switches(self):
        self.closed_switches = get_cond_list(1, self.switches_obs)
        self.opened_switches = get_cond_list(0, self.switches_obs)

    def sort_opened_switches(self):
        return self.opened_switches.sort()
    
    # --------------------------------
    # FAILURE's METHODS
    # --------------------------------
    def do_failure(self, line):
        self.open_switch(line)


class ToPython:

    def __init__(self, nodes, switches, tie, conn):
        self.nodes = nodes
        self.switches = switches
        self.tie = tie
        self.conn = conn

    def get_conn(self):
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
        return tie

    def get_switches(self):
        switches = [1 for x in range(len(self.switches))]
        tie = self.get_tie()
        for x in tie:
            switches[x] = 0
        return switches

    def get_nodes(self):
        # TODO: update nodes values certainly
        nodes = [0 for x in range(len(self.nodes))]
        return nodes

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


# Methods to used across
def find_pos(elements, element): return elements.index(element)


def fin_element(elements, pos): return elements[pos]


def get_cond_list(cond, arg):
    """ Create a list with the names of the elements
    that satisfy a condition
    :param cond: conditional to add element to the list
    :param arg: list to evaluate
    :return: a list with the names of the switches
    satisfy the condition
    """
    new_list = []
    index = 0
    for i in arg:
        if i == cond:
            new_list.append(index)
        index += 1
    return new_list
