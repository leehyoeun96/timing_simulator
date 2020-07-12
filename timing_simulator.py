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
        print("currunt system time", curr_t)
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
    task.art = curr_time
    return task

def execute_task(tasks, cpu, queue, prio_set, curr_time):
    next_task_name = queue.pop(0)
    cpu = next_task_name
    tasks[next_task_name] = update_task_status(task_set[next_task_name], curr_time)
    return cpu

def initialize_system(queue, cpus, tasks, prio_set, curr_time):
    initialize_tasks(tasks, prio_set)
    #print(prio_set)

    affi = 0 #USE ONLY 1 CPU
    #for affi in range(len(cpus)):
    for attr in tasks.values():
        insert_task_in_queue(queue[affi], prio_set, attr.name)
    #print(queue)
    if queue[affi] : cpus[affi] = execute_task(tasks, cpus[affi], queue[affi], prio_set, curr_time)
    else : print("There's no ready task in run queue")
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
    next_off = 0
    run_task = cpus[affi]
    run_task_prio = prio_set[cpus[affi]]
    ready_task_prio = prio_set[queue[affi][0]]
   
    if run_task_prio <= ready_task_prio:
        print("not preemption!")
        next_off = task_set[run_task].ext
        print("next_off: ",next_off)
        return next_off
    #else:
        

    print("min")
    return 1

def update_system_status(curr_t, next_off, queue, cpus, tasks):
    print("update")

task_timing_simulation(run_q, cpus, task_set, prio_set)