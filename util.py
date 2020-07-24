###########################################
# utilities for printing
############################################
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

###########################################
# utilities for task processing
############################################
def insert_task_in_queue(name, affi, tasks, queue):
    if not name in tasks.keys() :
        print("This task is not in task_set")
        return
    queue[affi].append(name)
    update_task_status(name, tasks[name].art, tasks, 'ready')
    queue[affi].sort(key=lambda i : tasks[i].off + (tasks[i].prd * tasks[i].cnt))

def execute_task(ready_task, curr_time, affi, tasks, cpus):
    update_task_status(ready_task, curr_time, tasks, 'run')
    cpus[affi] = ready_task

def update_task_status(task_name, arrival_time, tasks, status):
    task = tasks[task_name]
    task.stt = status
    task.art = arrival_time
