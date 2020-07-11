from recordtype import recordtype

ncpus = 1
cpus = ['task_0' for x in range(ncpus)]
run_q = [list() for x in range(ncpus)]

task_attr = recordtype("task_attr", 'name, ext, art, prd, off, rtd, stt')

prio_set = dict()
task_set = {
    'task_A': task_attr(name='task_A',   ext=5,  art=0,  prd=100, off=0,  rtd=0, stt='ready'),
    'task_B': task_attr(name='task_B',   ext=5,  art=0,  prd=25,  off=0,  rtd=0, stt='ready'),
    'task_C': task_attr(name='task_C',   ext=5,  art=0,  prd=10,  off=0,  rtd=0, stt='ready')
}

def task_timing_simulation(run_q, cpus, task_set, prio_set):
    curr_t = 0
    next_off = 0
    initialize_system(run_q, cpus, task_set, prio_set, curr_t)
    print_cpu_status("cpu status after initialize: ", cpus)
    print_task_status("task status after initialize", task_set)
    while curr_t < 1:
        next_off = find_min_event_time(run_q, cpus, task_set, prio_set)
        update_system_status(curr_t, next_off, run_q, cpus, task_set)
        curr_t = curr_t + next_off

def initialize_tasks(tasks, prio):
    for name, attr in tasks.items():
        prio[name] = attr.prd
        attr.art = attr.off

def insert_task_in_queue(queue, prio_set, name):
    queue.append(name)
    queue.sort(key=lambda i : prio_set[i])

def update_task_status(task, curr_time):
    task.stt = 'run'
    curr_time = task.art
    task.art = task.art + task.prd
    return task

def execute_task(cpu, queue, prio_set, curr_time):
    next_task_name = queue.pop(0)
    cpu = next_task_name
    task_set[next_task_name] = update_task_status(task_set[next_task_name], curr_time)
    return cpu

def initialize_system(queue, cpus, tasks, prio_set, curr_time):
    initialize_tasks(tasks, prio_set)
    #print(prio_set)

    affi = 0 #USE ONLY 1 CPU
    #for affi in range(len(cpus)):
    for attr in tasks.values():
        insert_task_in_queue(queue[affi], prio_set, attr.name)
    #print(queue)
    if queue[affi] : cpus[affi] = execute_task(cpus[affi], queue[affi], prio_set, curr_time)
    print("init END")

def print_cpu_status(comment, cpus):
    print("+++",comment,"+++")
    for cpu_idx in range(len(cpus)):
        print("CPU #",cpu_idx, " status:", cpus[cpu_idx])
    print()

def print_task_status(comment, task_set):
    print("+++",comment,"+++")
    for task in task_set.values():
        print(task.name, " status:", task.stt,", arrival time:", task.art)
    print()

def find_min_event_time(queue, cpus, tasks, prio_set):
    affi = 0 #USE ONLY 1 CPU
    #CASE 1: preemption
    #Priority of running task is lower than minimum priority of ready tasks.
    print(prio_set[cpus[affi]])
    next_task = queue[affi].pop(0)
    print(prio_set[next_task])
    if prio_set[cpus[affi]] < prio_set[next_task]:
        print("preemption!")
    #Arrival time of the ready task is lower than finish time of running task.
    ##YOU NEED THINK ABOUT TIMING PROBLEM IN TWO TASKS (LIKE USING ABSOULTE TIME OR RELATIVE TIME.. OR RELATION BETWEEN ART, RTD..)
    
    #CASE 2: termination
    print("min")
    return 1

def update_system_status(curr_t, next_off, queue, cpus, tasks):
    print("update")

task_timing_simulation(run_q, cpus, task_set, prio_set)