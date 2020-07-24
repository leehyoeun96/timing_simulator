import util as util

def initialize_system(curr_time, affi, tasks, priorities, cpus, queue):
    if len(tasks) == 0:
        print("There's no task in task set")
        exit()
    for name, attr in tasks.items():
        priorities[name] = attr.prd
        attr.ret = attr.ext
    
    #for affi in range(len(cpus)):
    for attr in tasks.values():
        util.insert_task_in_queue(attr.name, affi, tasks, queue)
    if queue[affi] : 
        ready_task=queue[affi].pop(0)
        util.execute_task(ready_task, curr_time, affi, tasks, cpus)
    else : print("There's no ready task in run queue")

def find_min_event_time(current_t, affi, tasks, priorities, cpus, queue):
    next_evt_list = []
    if not queue[affi]:
        print("There's no tasks in run queue")
        exit()
    
    run_task = cpus[affi]
    #print(tasks[run_task])
    terminate_t = tasks[run_task].art + tasks[run_task].ret
    #print(run_task,"'s terminate time:",terminate_t)
    for ready_task in queue[affi]:
        release_t = (tasks[ready_task].prd * tasks[ready_task].cnt) + tasks[ready_task].off
        #print(ready_task, "'s release time:",release_t)
        if run_task not in tasks.keys(): #next task is first task after cpu idle time
            next_evt = release_t
        elif priorities[run_task] <= priorities[ready_task]:
            next_evt = max(release_t, terminate_t)
        elif terminate_t <= release_t:
            next_evt = release_t
        else:                        #Occur preemption
            next_evt = max(release_t, current_t)
        next_task = ready_task
        next_evt_list.append((next_evt,next_task))
    
    #HMMMM.....
    next_evt = (tasks[run_task].prd * (tasks[run_task].cnt+1)) + tasks[run_task].off
    next_task = run_task
    next_evt_list.append((next_evt,next_task))
    
    min_next_evt = min(next_evt_list)
    
    return min_next_evt

def update_system_status(curr_t, next_evt, next_task, affi, tasks, priorities, cpus, queue):
    next_off = next_evt - curr_t
    run_task = cpus[affi]

    #if next_task not in queue[affi]:
    if next_task not in tasks:
        print("The next task is not in run queue:", next_task)
        exit()
    if next_off < 0:
        print("It seems strange...next offset is negative value", next_off)
        exit()
    
    if next_off < tasks[run_task].ret: #Occur preemption
        #print("occur preemption!")
        tasks[run_task].ret = tasks[run_task].ext - next_off
    else:
        #print("terminate normally")
        calculate_response_time(run_task, tasks)
        tasks[run_task].ret = tasks[run_task].ext
        tasks[run_task].cnt = tasks[run_task].cnt + 1
    util.insert_task_in_queue(run_task, affi, tasks, queue)
    next_task = queue[affi].pop(queue[affi].index(next_task))
    util.execute_task(next_task, next_evt, affi, tasks, cpus)

def calculate_response_time(task, tasks):
    print("*******************************")
    print("task name: ",tasks[task].name)
    arrival_time = tasks[task].art
    print("latest arrival time",arrival_time)
    release_time = (tasks[task].prd * tasks[task].cnt) + tasks[task].off
    print("release time", release_time)
    remaining_excution_time = tasks[task].ret
    print("remainig excution time", remaining_excution_time)
    response_time = arrival_time - release_time + remaining_excution_time
    print("response time", response_time)
    print("*******************************")
