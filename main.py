from recordtype import recordtype
from simcpu import *
from simsys import *
import util as util

task_feat = recordtype("task_attr", 'ext, prd, off, aff')

cur_time = 0
max_time = 99
ncpus = 1

feature_set = {
    'task_A': task_feat(ext=5, prd=100, off=5, aff=0),
    'task_B': task_feat(ext=5, prd=25,  off=0, aff=0),
    'task_C': task_feat(ext=5, prd=10,  off=2, aff=0)
}

def sys_simulation(ncpus):
    simsys = SIMSYS(ncpus, feature_set, cur_time, max_time)
    simsys.initialize_system()
   
    while simsys.current_time < simsys.max_time:
        print("---------------------------")
        cpu_idx, next_evt = simsys.find_min_event_time()
        next_time, next_task = next_evt
        end_task = simsys.cpus[cpu_idx].update_cpu_status(next_time, next_task)
        #update_system_status(end_task)
        simsys.current_time = next_time
        simsys.cpus[cpu_idx].print_status("")
    return simsys.rtl

response_time_list = sys_simulation(ncpus)

util.show_response_time(response_time_list)
print_task_status("after main",task_set)