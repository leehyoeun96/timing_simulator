from recordtype import recordtype
from simcpu import *
import util as util

task_attr = recordtype("task_attr", 'name, ext, ret, art, prd, cnt, off, rtd, stt')
'''
ext = excution time
ret = remaining excution time
art = latest arrival time
prd = period
cnt = period count
off = offset
rtd = response time distribution
stt = status
'''

current_time = 0
prio_set = dict()
task_set = {
    'task_A': task_attr(name='task_A', ext=5, ret=0, art=0, prd=100, cnt=0, off=5, rtd=0, stt='ready'),
    'task_B': task_attr(name='task_B', ext=5, ret=0, art=0, prd=25,  cnt=0, off=0, rtd=0, stt='ready'),
    'task_C': task_attr(name='task_C', ext=5, ret=0, art=0, prd=10,  cnt=0, off=2, rtd=0, stt='ready')
}

cpu_idx = 0
simcpu = SIMCPU(cpu_idx, prio_set, task_set, current_time)
response_time_list = simcpu.main()
util.show_response_time(response_time_list)
print_task_status("after main",task_set)