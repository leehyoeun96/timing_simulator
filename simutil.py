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

def print_response_time(comment, task, release_t):
    print("*******",comment,"*******")
    print("  task name:",task.name)
    print("  latest arrival time:",task.art)
    print("  remaining excution time:", task.ret)
    print("  release time:", release_t)
    print("  response time:", task.rtd)
    print("*****************************")
    print()

def print_message(msg):
    print("----------Message-----------")
    print("  sources:", msg.src)
    print("  msg ids:", msg.id)
    print("  start time:", msg.start)
    print("  end time:", msg.end)
    '''
    for idx, itm in enumerate(msg.interm):
        print("  intermediates", idx, ":",itm)
    '''
    print("----------------------------")

def show_time_list(response_time):
    if len(response_time) == 0:
        print("ERROR: Response time was NOT SAVED")
        exit()
    for task, time in response_time.items():
        print(task, time)
    #plt.hist(response_time, bins = len(response_time))
    #plt.show()

def get_e2el_from_msg(msgs):
    e2eL = {}
    for msg in msgs:
        for idx, src in enumerate(msg.src):
            if src in e2eL.keys():
                e2eL[src].append(msg.end-msg.start[idx])
            else:
                e2eL[src] = [msg.end-msg.start[idx]]
    '''
    for task, e2el in e2eL.items():
        print(task,e2el)
    '''
    return e2eL

def show_graph(e2eL_dict):
    for task, e2el in e2eL_dict.items():
        plt.clf()
        alpha = 1
        title = "End to end latency:"+task
        plt.hist(e2el, align ='mid', bins=len(e2el), density=False)
        plt.grid()					
        plt.xlabel('execution time')
        plt.ylabel('probability')
        plt.title(title)
        plt.show()

def show_multi_cdf(title, dists):
        if len(dists) <= 1: return False
        alpha = 1
        color_list = ['b', 'r', 'g']
        for task, dist in dists.items():
            #Plotting analyzation result.
            idx = 0
            plt.plot(range(len(dist[idx])), dist[idx], color=color_list[idx%len(color_list)], alpha=alpha, label=task+" "+'analyzation')
            #Plotting simulation result.
            idx = 1
            plt.plot(range(len(dist[idx])), dist[idx], color=color_list[idx%len(color_list)], alpha=alpha, label=task+" "+'simulation')

            plt.grid()					
            plt.legend(loc="lower right")
            plt.xlabel('time')
            plt.ylabel('CDF')
            plt.title(title)
            plt.show()
            plt.clf()
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
        print("Define ext_table about", name)
        exit()
    if not sum(table[name])==1:
        print(name, "'s total probaility is not 1")
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