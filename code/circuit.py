import numpy as np


class Circuit:

    def __init__(self, voltages):
        self.voltages = voltages

    def check_voltages_limits(self):
        check = False
        for i in self.voltages:
            if 0.95 > i > 1.05:
                check = True
                break
        return check
