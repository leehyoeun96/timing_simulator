from recordtype import recordtype
from simsys import *
import time
import util as util

task_feat = recordtype("task_feat", 'prd, off, aff')

max_time = 100

task_graph = {
    'task_0': ['STC', 'XGF', 'F2G', 'QTC', 'DND'],
    'STC': ['EKF'],
    'EKF': ['GEN'],
    'GEN': ['TEV'],
    'XGF': ['NDT'],
    'F2G': ['NDT'],
    'NDT': ['EKF'],
    'QTC': ['UKF'],
    'UKF': ['RVF'],
    'DND': ['VBT'],
    'VBT': ['RVF'],
    'RVF': ['OMP'],
    'OMP': ['TEV'],
    'TEV': ['BSE'],
    'BSE': ['PPS'],
    'PPS': ['task_0'],
}
feature_set = {
    'STC': task_feat(prd=10, off=0, aff=4),
    'EKF': task_feat(prd=10, off=0, aff=5),
    'GEN': task_feat(prd=10, off=0, aff=6), 
    'XGF': task_feat(prd=100, off=0, aff=1),
    'F2G': task_feat(prd=100, off=0, aff=2),
    'NDT': task_feat(prd=100, off=0, aff=1),
    'QTC': task_feat(prd=100, off=0, aff=2),
    'UKF': task_feat(prd=100, off=0, aff=2),
    'DND': task_feat(prd=50, off=0, aff=3),
    'VBT': task_feat(prd=50, off=0, aff=3),
    'RVF': task_feat(prd=50, off=0, aff=3),
    'OMP': task_feat(prd=50, off=0, aff=3),
    'TEV': task_feat(prd=10, off=0, aff=6),
    'BSE': task_feat(prd=10, off=0, aff=6),
    'PPS': task_feat(prd=10, off=0, aff=6),
}
ext_table = {
    'STC': [0, 0, 1],
    'EKF': [0, 0, 1],
    'GEN': [0, 0, 1], 
    'XGF': [0, 0, 0, 0, 0, 1], 
    'F2G': [0, 0, 0, 0, 0, 1],
    'NDT': [0, 0, 0, 0, 0, 1],
    'QTC': [0, 0, 0, 0, 0, 1],
    'UKF': [0, 0, 0, 0, 0, 1],
    'DND': [0, 0, 0, 1],
    'VBT': [0, 0, 0, 1],
    'RVF': [0, 0, 0, 1],
    'OMP': [0, 0, 0, 1],
    'TEV': [0, 0, 1],
    'BSE': [0, 0, 1],
    'PPS': [0, 0, 1],
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