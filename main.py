from recordtype import recordtype
from simsys import *
import time
import util as util

task_feat = recordtype("task_feat", 'prd, off, aff')

cur_time = 0
max_time = 100
ncpus = 1

task_graph = {
    'task_0': ['task_A', 'task_B'],
    'task_A': ['task_C'],
    'task_B': ['task_C'],
    'task_C': ['task_0']
}

feature_set = {
    'task_A': task_feat(prd=100, off=0, aff=0),
    'task_B': task_feat(prd=25,  off=0, aff=0),
    'task_C': task_feat(prd=25,  off=0, aff=0)
}

ext_table = {
    'task_A': [0, 0.1, 0.1, 0, 0.2, 0.3, 0.2, 0.1],
    'task_B': [0, 0.1, 0.1, 0.3, 0.1, 0.2, 0.1, 0.1],
    'task_C': [0, 0.1, 0.3, 0.3, 0.2, 0.1],
}

ext_table = {
    'task_A': [0, 1],
    'task_B': [0, 0, 1],
    'task_C': [0, 0, 0, 1],
}

def sys_simulation():
    simsys = SIMSYS(ncpus, feature_set, ext_table, task_graph, cur_time, max_time)
    simsys.initialize_system()
    
    while simsys.current_time < simsys.max_time:
        print("---------------------------")
        cpu_idx, next_evt = simsys.find_min_event_time()
        simsys.update_system_status(cpu_idx, next_evt)
        simsys.cpus[cpu_idx].print_status("")
        #input()
    return simsys.gathered_rtl

response_time_list = sys_simulation()
util.show_response_time(response_time_list)