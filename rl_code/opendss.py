
import numpy as np
# OpenDSSCOM packages
import sys 
#assert ('wind32' in sys.platform), 'Opendss runs on Windows only.'
from win32com.client import makepy
import win32com.client

class OpenDSSCircuit:

    def __init__(self, ties):
        self.com = OpenDSSG()
        self.com.solve()
        # num_tie = ties
        self.lines = self.com.get_lines()
        self.num_switches = len(self.lines)
        self.nodes = self.com.get_buses()
        self.num_nodes = len(self.nodes)
        self.ties = self.lines[self.num_switches-num_tie:self.num_switches]

        for x in self.ties:
            self.open_switch(x)
            self.com.solve()

    def open_init(self):
        self.com.com_init()
        for x in self.ties:
            self.open_switch(x)
        self.com.solve()



    def get_conn(self): # todo obtener la matrix de incidencia
        """Get line connection scheme between nodes
        :return conn: (tuple 2d) line connections
        """
        conn = []
        for x in self.lines:
            self.set_active_line(x)
            nodes = self.get_conn_element()
            aux = []
            for y in nodes:
                aux.append(y.split('.')[0])
            conn.append(tuple(aux))
        return tuple(conn)




    def com_init(self): # todo hcaer metodo que reestablesca los valores de fabrica del modelo
        self.send_command('ClearAll')
        self.DSSText.Command = 'compile ' + self.path


    def ae_is_open(self): # todo verifica diferente
        """Verify is active element is opened
        :return: [boolean, boolean]"""
        term1 = self.DSSCktElement.IsOpen(1, 0)
        term2 = self.DSSCktElement.IsOpen(2, 0)
        return [term1, term2]
