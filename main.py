from recordtype import recordtype
from simsys import *
import util as util

task_feat = recordtype("task_feat", 'ext, prd, off, aff')

cur_time = 0
max_time = 50
ncpus = 1

feature_set = {
    'task_A': task_feat(ext=10,prd=100, off=0, aff=0),
    'task_B': task_feat(ext=5, prd=25,  off=0, aff=0),
    'task_C': task_feat(ext=7, prd=10,  off=0, aff=0)
}

lookup_table = {
    'task_A': [ (5, 0.5), 
                (10, 0.5), ],
    'task_B': [ (5, 0.5), 
                (10, 0.5), ],
    'task_C': [ (5, 0.5), 
                (7, 0.5), ],
} 
'''
lookup_table = {
    'task_A': [ (3, 0.25), 
                (5, 0.5),
                (9, 0.25)],
    'task_B': [ (1, 0.2), 
                (2, 0.2), 
                (3, 0.2), 
                (4, 0.2), 
                (5, 0.2)],
    'task_C': [ (2, 0.125), 
                (4, 0.125), 
                (6, 0.25), 
                (8, 0.25), 
                (10, 0.125), 
                (11, 0.125)]
}
'''

def sys_simulation():
    simsys = SIMSYS(ncpus, feature_set, lookup_table, cur_time, max_time)
    simsys.initialize_system()
    
    while simsys.current_time < simsys.max_time:
        print("---------------------------")
        cpu_idx, next_evt = simsys.find_min_event_time()
        simsys.update_system_status(cpu_idx, next_evt)
        simsys.cpus[cpu_idx].print_status("")
        input('').split(" ")[0]
    return simsys.gathered_rtl

response_time_list = sys_simulation()
util.show_response_time(response_time_list)