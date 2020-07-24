from recordtype import recordtype

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

def initialize_tasks(tasks, prio):
    if len(tasks) == 0:
        print("There's no task in task set")
        exit()
    for name, attr in tasks.items():
        prio[name] = attr.prd
        attr.ret = attr.ext

def insert_task_in_queue(name, affi):
    if not name in task_set.keys() :
        print("This task is not in task_set")
        return
    run_q[affi].append(name)
    update_task_status(name, task_set[name].art, 'ready')
    run_q[affi].sort(key=lambda i : task_set[i].off + (task_set[i].prd * task_set[i].cnt))

def update_task_status(task_name, arrival_time, status):
    task = task_set[task_name]
    task.stt = status
    task.art = arrival_time

def execute_task(ready_task, curr_time, affi):
    update_task_status(ready_task, curr_time, 'run')
    cpus[affi] = ready_task

def print_queue(comment, queue):
    print("+++",comment,"+++")
    for idx in range(len(queue)):
        print("Queue #",idx,"task:",queue[idx])
    print()

def print_cpu_status(comment, cpus):
    print("+++",comment,"+++")
    for cpu_idx in range(len(cpus)):
        print("CPU #",cpu_idx, " status:", cpus[cpu_idx])
    print()

def print_task_status(comment, task_set):
    print("+++",comment,"+++")
    for task in task_set.values():
        print(task.name)
        print("  status:", task.stt,", arrival time:", task.art)
        #print("  arrival time:", task.art)
        print("  remaining time:", task.ret)
    print()

def find_min_event_time(current_t, affi):
    next_evt_list = []
    if not run_q[affi]:
        print("There's no tasks in run queue")
        exit()
    
    run_task = cpus[affi]
    #print(task_set[run_task])
    terminate_t = task_set[run_task].art + task_set[run_task].ret
    #print(run_task,"'s terminate time:",terminate_t)
    for ready_task in run_q[affi]:
        release_t = (task_set[ready_task].prd * task_set[ready_task].cnt) + task_set[ready_task].off
        #print(ready_task, "'s release time:",release_t)
        if run_task not in task_set.keys(): #next task is firtst task after cpu idle time
            next_evt = release_t
        elif prio_set[run_task] <= prio_set[ready_task]:
            next_evt = max(release_t, terminate_t)
        elif terminate_t <= release_t:
            next_evt = release_t
        else:                        #Occur preemption
            next_evt = max(release_t, current_t)
        next_task = ready_task
        next_evt_list.append((next_evt,next_task))
    
    #HMMMM.....
    next_evt = (task_set[run_task].prd * (task_set[run_task].cnt+1)) + task_set[run_task].off
    next_task = run_task
    next_evt_list.append((next_evt,next_task))
    
    min_next_evt = min(next_evt_list)
    
    return min_next_evt

def update_system_status(curr_t, next_evt, next_task, affi):
    next_off = next_evt - curr_t
    run_task = cpus[affi]

    #if next_task not in run_q[affi]:
    if next_task not in task_set:
        print("The next task is not in run queue:", next_task)
        exit()
    if next_off < 0:
        print("It seems strange...next offset is negative value", next_off)
        exit()
    
    if next_off < task_set[run_task].ret: #Occur preemption
        print("occur preemption!")
        task_set[run_task].ret = task_set[run_task].ext - next_off
    else:
        print("terminate normally")
        calculate_response_time(run_task)
        task_set[run_task].ret = task_set[run_task].ext
        task_set[run_task].cnt = task_set[run_task].cnt + 1
    insert_task_in_queue(run_task, affi)
    next_task = run_q[affi].pop(run_q[affi].index(next_task))
    execute_task(next_task, next_evt, affi)

def calculate_response_time(task):
    print("*******************************")
    print("task name: ",task_set[task].name)
    arrival_time = task_set[task].art
    print("latest arrival time",arrival_time)
    release_time = (task_set[task].prd * task_set[task].cnt) + task_set[task].off
    print("release time", release_time)
    remaining_excution_time = task_set[task].ret
    print("remainig excution time", remaining_excution_time)
    response_time = arrival_time - release_time + remaining_excution_time
    print("response time", response_time)
    print("*******************************")


def initialize_system(curr_time, affi):
    initialize_tasks(task_set, prio_set)
    #print(prio_set)

    #for affi in range(len(cpus)):
    for attr in task_set.values():
        insert_task_in_queue(attr.name, affi)
    if run_q[affi] : 
        ready_task=run_q[affi].pop(0)
        execute_task(ready_task, curr_time, affi)
    else : print("There's no ready task in run queue")

def task_timing_simulation():
    curr_t = 0
    next_evt = 0
    affi = 0 #USE ONLY 1 CPU
    next_task = 'task_0'
    initialize_system(curr_t, affi)
    print_cpu_status("cpu status after initialize ", cpus)
    print_task_status("task status after initialize", task_set)
    print_queue("queue after initialize", run_q[affi])
    while curr_t < 100:
        print("-------------------------------")
        next_evt, next_task = find_min_event_time(curr_t, affi)
        update_system_status(curr_t, next_evt, next_task, affi)
        
        #print("current system time", curr_t)
        #print("time to next event ", next_evt)
        curr_t = next_evt
        
        print_cpu_status("cpu status ", cpus)
        print_task_status("task status ", task_set)
        print_queue("queue", run_q[affi])
        input('').split(" ")[0]	

task_timing_simulation()