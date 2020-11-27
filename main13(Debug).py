from recordtype import recordtype
from simsys import *
import time
import util as util

task_feat = recordtype("task_feat", 'prd, off, aff')

max_time = 200

task_graph = {
    'task_0': ['task_A', 'task_B', 'task_C'],
    'task_A': ['task_D'],
    'task_B': ['task_E'],
    'task_C': ['task_F'],
    'task_D': ['task_E'],
    'task_E': ['task_G'],
    'task_F': ['task_G'],
    'task_G': ['task_H'],
    'task_H': ['task_0'],
}
feature_set = {
    'task_A': task_feat(prd=200, off=0, aff=0),
    'task_B': task_feat(prd=100, off=0, aff=1),
    'task_C': task_feat(prd=70, off=0, aff=2),
    'task_D': task_feat(prd=60, off=0, aff=3),
    'task_E': task_feat(prd=60, off=0, aff=3),
    'task_F': task_feat(prd=60, off=0, aff=3),
    'task_G': task_feat(prd=60, off=0, aff=3),
    'task_H': task_feat(prd=60, off=0, aff=3),
}
ext_table = {
    'task_A': [0, 1],
    'task_B': [0, 0, 1],
    'task_C': [0, 0, 0, 1],
    'task_D': [0, 1],
    'task_E': [0, 0, 1],
    'task_F': [0, 0, 0, 1],
    'task_G': [0, 0, 0, 1],
    'task_H': [0, 0, 0, 1],
}

def sys_simulation():
    simsys = SIMSYS(feature_set, ext_table, task_graph, max_time)
    simsys.initialize_system()
    
    while simsys.current_time < simsys.max_time:
        #print("...........................")
        cpu_list, next_time, next_tasks = simsys.find_min_event_time()
        simsys.update_system_status(cpu_list, next_time, next_tasks)
        '''
        for cpu_idx in cpu_list:
            simsys.cpus[cpu_idx].print_status("")
        #input()
        '''
    return simsys.gathered_rtl, simsys.gathered_msg

response_time_list, e2eL_msgs = sys_simulation()
'''
print("*Final response time")
util.show_response_time(response_time_list)
print()
'''
print("*Final e2e latency")
for msg in e2eL_msgs: print_message(msg)
print()
e2e_dict = util.show_e2el(e2eL_msgs)
#util.show_graph(e2e_dict)