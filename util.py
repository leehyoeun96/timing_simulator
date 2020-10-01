import matplotlib.pyplot as plt
import random

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
        print("  status:", task.stt)
        print("  arrival time:", task.art)
        print("  remaining time:", task.ret)
        print("  execution time:", task.ext)
    print()

def print_message(comment, msg):
    print("+++",comment,"+++")
    print("  sources:", msg.src)
    print("  msg_ids:", msg.id)
    print("  start_t:", msg.start)
    print("  end_time:", msg.end)
    print()

def show_response_time(response_time):
    if len(response_time) == 0:
        print("ERROR: Response time was NOT SAVED")
        exit()
    print(response_time)
    plt.hist(response_time, bins = len(response_time))
    #plt.show()

###########################################
# utilities for task processing
############################################

def update_task_status(task_name, arrival_time, tasks, status):
    task = tasks[task_name]
    task.set_stt(status)
    task.set_art(arrival_time)
    return task_name

def sampling_ext(table, name):
    ###
    ##Generate real number randomly.
    ##And lookup sampling table.
    ###
    if not name in table:
        print("Define lookup table about", name)
        exit()
    if sum(table[name]) >1:
        print(name, "'s total probaility is over 1")
        exit()
    ext_sample = 0
    real = random.random()
    cml_prob = 0
    #print(name)
    for time, prob in enumerate(table[name]):
        cml_prob = cml_prob + prob
        cml_prob = round(cml_prob, 10)
        if max(real, cml_prob) != real:
            ext_sample = time
            break
    return ext_sample