import numpy as np


class DistributionSystem:

    def __init__(self, nodes, switches, tie):
        self.nodes_name = nodes  # Node list
        self.lines_name = switches  # Line list
        self.loads_name = None  # Load list
        self.switches_name = switches  # Switches list
        self.start_tie = tie  # Tie switches list
        self.switches_num = len(switches)
        self.failure = None  # Line failure
        self.switches_obs = []  # Switches state
        self.failures_obs = []
        self.opened_switches = []
        self.closed_switches = []

        self.sys_start()

    def sys_start(self):
        # Fill 1 for sectionalizing switch
        self.switches_obs = [1 for x in range(self.switches_num)]

        # Fill 0 for tie switches in switches_obs
        for i in range(len(self.start_tie)):
            pos = find_element(self.switches_name, self.start_tie[i])
            self.switches_obs[pos] = 0

        self.update_switches()

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

    def open_switch(self, switch):
        """Open a switch
        :param switch: index of the switch in switches_name
        """
        obs = self.switches_obs
        if 0 <= switch < len(obs):
            obs[switch] = 0
        self.update_switches()

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
        """Find the switche name
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



