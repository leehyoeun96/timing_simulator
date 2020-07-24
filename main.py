from recordtype import recordtype
import util as util
import timing_simulator as tsim

ncpus = 1
cpus = [0 for x in range(ncpus)]
run_q = [list() for x in range(ncpus)]

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

prio_set = dict()
task_set = {
    'task_A': task_attr(name='task_A', ext=5, ret=0, art=0, prd=100, cnt=0, off=5, rtd=0, stt='ready'),
    'task_B': task_attr(name='task_B', ext=5, ret=0, art=0, prd=25,  cnt=0, off=0, rtd=0, stt='ready'),
    'task_C': task_attr(name='task_C', ext=5, ret=0, art=0, prd=10,  cnt=0, off=2, rtd=0, stt='ready')
}

def task_timing_simulation():
    curr_t = 0
    next_evt = 0
    affi = 0 #USE ONLY 1 CPU
    next_task = 'task_0'
    tsim.initialize_system(curr_t, affi, task_set, prio_set, cpus, run_q)
    util.print_cpu_status("cpu status after initialize ", cpus)
    util.print_task_status("task status after initialize", task_set)
    util.print_queue("queue after initialize", run_q[affi])
    while curr_t < 100:
        print("-------------------------------")
        next_evt, next_task = tsim.find_min_event_time(curr_t, affi, task_set, prio_set, cpus, run_q)
        tsim.update_system_status(curr_t, next_evt, next_task, affi, task_set, prio_set, cpus, run_q)
        
        #print("current system time", curr_t)
        #print("time to next event ", next_evt)
        curr_t = next_evt
        
        util.print_cpu_status("cpu status ", cpus)
        util.print_task_status("task status ", task_set)
        util.print_queue("queue status", run_q[affi])
        input('').split(" ")[0]	

task_timing_simulation()