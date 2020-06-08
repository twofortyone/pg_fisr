import pandas as pd
import numpy as np
from training.com import OpenDSSCOM
from training.tenv import FisrEnvironment
from production.penv import PFisrEnvironment
from production.tcp import OpenDSSG

ts_df = pd.read_feather('E:/pg_fisr/data/123_06022020_nsimulation/ieee123bus_terminal_states_2020-06-02.ftr')
term_states = ts_df.values.tolist()
com = OpenDSSCOM('E:/pg_fisr/data/models/IEEE_123_FLISR_Case/Master.DSS')
env = FisrEnvironment(com,[],[],[])

ss = []
for i,term in enumerate(term_states):
    env.failure = i
    aux = env.get_ss_from_state(term[0]).tolist()
    ss.append(aux)

ss = np.asarray(ss)

ss_df = pd.DataFrame(data=ss, columns=com.switches)
ss_df.to_feather('E:/term_states.ftr')

# -------------------------------------------
tcp = OpenDSSG()
aux = []
for i, sw in enumerate(tcp.switches):
    aux.append(ss_df[sw].tolist())
aux = np.asarray(aux).transpose()

penv = PFisrEnvironment([])
aux2 = aux.tolist()
terminal_states = []
for i, cs in enumerate(aux2):
    current_state = str(cs).strip('[]').replace(',', '').replace(' ', '')
    sspos = penv.switch_states_dict[current_state]
    terminal_states.append(i*penv.num_switch_states + sspos)

term_df = pd.DataFrame(data=terminal_states,columns= ['ts'])
term_df.to_feather('E:/term_states_dss2g.ftr')
