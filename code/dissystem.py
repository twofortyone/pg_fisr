import numpy as np


class DistributionSystem:

    def __init__(self, nodes, switches, tie, conn):
        self.nodes_name = nodes  # Node list
        self.nodes_number = len(self.nodes_name)
        self.lines_name = switches  # Line list
        self.loads_name = None  # Load list
        self.switches_name = switches  # Switches list
        self.start_tie = tie  # Tie switches list
        self.switches_num = len(switches)
        self.failure = None  # Line failure
        self.switches_obs = []  # Switches state
        self.failures_obs = []
        self.nodes_adj_matrix = None
        self.opened_switches = []
        self.closed_switches = []
        self.nodes_conn_names = conn
        self.sw_nodes_conn = []

        self.sys_start()

    def sys_start(self):
        # Fill 1 for sectionalizing switch
        self.switches_obs = [1 for x in range(self.switches_num)]

        # Fill 0 for tie switches in switches_obs
        for i in range(len(self.start_tie)):
            pos = find_element(self.switches_name, self.start_tie[i])
            self.switches_obs[pos] = 0

        self.update_switches()
        self.sw_nodes_conn = name_node_conecction_2numnc(self.nodes_conn_names, self.nodes_name)
        self.nodes_adj_matrix = self.create_adjacency_matrix()

    # def possible_close_actions(self, current_):
    #     switches = self.switches_obs
    #     actions = []
    #     for i in range(len(switches)):
    #         if i != current_ and switches[i] == 0:
    #             actions.append(i)
    #     return actions
    #
    # def possible_open_actions(self, current_switches):
    #     cs = current_switches
    #     to_open = self.closed_switches.copy()
    #     for i in cs:
    #         if i in to_open:
    #             to_open.remove(i)
    #     return to_open

    # Action methods
    def close_switch(self, switch):
        """Close a switch
        :param switch: index of the switch in switches_name
        """
        obs = self.switches_obs
        if 0 <= switch < len(obs):
            obs[switch] = 1
        self.update_switches()
        self.connect_nodes(switch)

    def open_switch(self, switch):
        """Open a switch
        :param switch: index of the switch in switches_name
        """
        obs = self.switches_obs
        if 0 <= switch < len(obs):
            obs[switch] = 0
        self.update_switches()
        self.isolate_nodes(switch)

    def isolate_nodes(self, switch):
        nodes = self.sw_nodes_conn[switch]
        pos1 = nodes[0]
        pos2 = nodes[1]
        self.nodes_adj_matrix[pos1, pos2] = 0
        self.nodes_adj_matrix[pos2, pos1] = 0

    def connect_nodes(self, switch):
        nodes = self.sw_nodes_conn[switch]
        pos1 = nodes[0]
        pos2 = nodes[1]
        self.nodes_adj_matrix[pos1, pos2] = 1
        self.nodes_adj_matrix[pos2, pos1] = 1

    # def switch_node_off(self, node):
    #     """Disconnect a node passed as param
    #     :param node: index of the node to discconnect
    #     """
    #     obs = self.nodes_obs[node]
    #     if obs != 0:
    #         obs = 0
    #
    # def switch_node_on(self, node):
    #     """Disconnect a node passed as param
    #     :param node: index of the node to discconnect
    #     """
    #     obs = self.nodes_obs[node]
    #     if obs != 1:
    #         obs = 1

    def is_node_offline(self, node):
        """ Verify if there is at least one node offline"""
        check = True
        adj = self.nodes_adj_matrix
        for x in range(self.nodes_number):
            if adj[node, x] == 1:
                check = False
                break
        return check
    
    def create_adjacency_matrix(self):
        nm = self.nodes_number
        adj = np.zeros((nm, nm))
        ncn = self.nodes_conn_names
        nm = self.nodes_name
        sw_conn = name_node_conecction_2numnc(ncn, nm)

        for x in sw_conn:
            pos1 = x[0]
            pos2 = x[1]
            adj[pos1, pos2] = 1
            adj[pos2, pos1] = 1

        # TODO: update connection with tie stwiches

        return adj

    def update_switches(self):
        self.opened_switches = self.get_opened_switches()
        self.closed_switches = self.get_closed_switches()

    def sort_opened_switches(self):
        return self.opened_switches.sort()

    # Getters methods
    def get_opened_switches(self):
        """ Get the opened switches names
        :return: the opened switches list
        """
        obs = self.switches_obs
        return create_name_list(0, obs)

    def get_closed_switches(self):
        """ Get the closed switches names
        :return: the closed switches list
        """
        obs = self.switches_obs
        return create_name_list(1, obs)

    def get_switches_names(self, arg):
        """Find the switch name
        :param arg: switches_obs list
        :return names: list with tha names of the switches
        """
        names = []
        sn = self.switches_name
        for i in arg:
            names.append(sn[i])
        return names


# Methods to used across
def find_element(elements, element):
    """ Find element position
    :param elements: list to look from
    :param element:  element to look for
    :return: index of the element
    """
    return elements.index(element)


def create_name_list(cond, arg):
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


def name_node_conecction_2numnc(name_conns, nodes_name):
    """Converts a switch connection between nodes (names) 
    list to nodes (index) list  
    :param nodes_name:
    :param name_conns: list with node connections
    :return node_conn:
    """
    node_conn = []
    for x in name_conns:
        pos = []
        for j in x: 
            pos.append(find_element(nodes_name, j))
        node_conn.append(pos)
    return node_conn
