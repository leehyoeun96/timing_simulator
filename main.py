from recordtype import recordtype
from simcpu import *
from simsys import *
import util as util

task_feat = recordtype("task_attr", 'ext, prd, off, aff')

cur_time = 0
max_time = 99
ncpus = 2

feature_set = {
    'task_A': task_feat(ext=5, prd=100, off=5, aff=0),
    'task_B': task_feat(ext=5, prd=25,  off=0, aff=1),
    'task_C': task_feat(ext=5, prd=10,  off=2, aff=0)
}

def sys_simulation():
    simsys = SIMSYS(ncpus, feature_set, cur_time, max_time)
    simsys.initialize_system()
   
    while simsys.current_time < simsys.max_time:
        print("---------------------------")
        cpu_idx, next_evt = simsys.find_min_event_time()
        print("next time, next task", next_evt)
        simsys.update_system_status(cpu_idx, next_evt)
        simsys.cpus[cpu_idx].print_status("")
        input('').split(" ")[0]
    return simsys.gathered_rtl

response_time_list = sys_simulation()
util.show_response_time(response_time_list)