import matplotlib.pyplot as plt

###########################################
# utilities for printing
############################################
def print_queue(comment, queue):
    print("+++",comment,"+++")
    for idx in range(len(queue)):
        print("Queue #",idx,"task:",queue[idx])
    print()

def print_cpu_status(comment, running_task, cpu_idx):
    print("+++",comment,"+++")
    print("CPU #", cpu_idx, " status:", running_task)
    print()

def print_task_status(comment, task_set):
    print("+++",comment,"+++")
    for task in task_set.values():
        print(task.name)
        print("  status:", task.stt,", arrival time:", task.art)
        print("  remaining time:", task.ret)
    print()

def show_response_time(response_time):
    print(response_time)
    plt.hist(response_time, bins = len(response_time))
    #plt.show()

###########################################
# utilities for task processing
############################################
def insert_task_in_queue(name, tasks, queue):
    if not name in tasks.keys():
        print("This task is not in task_set")
        return
    queue.append(name)
    update_task_status(name, tasks[name].art, tasks, 'ready')
    queue.sort(key=lambda i : tasks[i].off + (tasks[i].prd * tasks[i].cnt))

def update_task_status(task_name, arrival_time, tasks, status):
    task = tasks[task_name]
    task.stt = status
    task.art = arrival_time
    return task_name
