from data.simulation import DataSimulation
from training.tenv import FisrEnvironment
from agents.fisr_agent_q import QLearningAgent
from training.tclass import Training
from training.tpclass import Production
from training.com import OpenDSSCOM
from training.tpenv import FisrEnvironment_Pro
import pandas as pd
from report.report import Report
from tqdm import trange
import time
import os

voltages = pd.read_feather('E:/pg_fisr/training/ieee123bus_voltages_2020-06-08.ftr').to_numpy()
iso_loads = pd.read_feather('E:/pg_fisr/training/ieee123bus_isolated_loads_2020-06-08.ftr').to_numpy()
num_loops = pd.read_feather('E:/pg_fisr/training/ieee123bus_num_loops_2020-06-08.ftr').to_numpy()

path = 'E:/pg_fisr/data/models/IEEE_123_FLISR_Case/Master.DSS'
this_path = os.path.abspath(os.path.dirname(__file__))
com = OpenDSSCOM(path)
ds = DataSimulation(this_path, com)
circuit_name = com.DSSCircuit.Name
env = FisrEnvironment(com, voltages, iso_loads, num_loops)
term_states = ds.get_terminal_states(env, iso_loads, voltages, num_loops)
print('finish')