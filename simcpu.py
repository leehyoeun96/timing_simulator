from util import *
from recordtype import recordtype

def calculate_response_time(task, tasks, response_list):
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
    response_list.append(response_time)
    
class SIMCPU(object):
    def __init__(self, cpu_idx, prio_set, task_set, cur_time, max_time):
        self.icpu = cpu_idx
        self.running_task = ''
        self.local_rq = list()

        self.rtl = list()
        self.prios = prio_set
        self.tasks = task_set
        self.current_time = cur_time
        self.max_time = max_time

    def initialize_cpu(self, tasks):
        if len(tasks) == 0:
            print("There's no task in task set")
            exit()
        
        #insert task in queue
        for name in tasks:
            insert_task_in_queue(name, self.tasks, self.local_rq)

        #allocate task to cpu
        if self.local_rq :
            ready_task=self.local_rq.pop(0)
            self.running_task = update_task_status(ready_task, self.current_time, self.tasks, 'run')
        else : print("There's no ready task in run queue")

    def find_min_event_time(self):
        next_evt_list = []
        if not self.running_task:
            print("There's no running task")
            return None
            #exit()

        run_task = self.running_task
        #print(self.tasks[run_task])
        terminate_t = self.tasks[run_task].art + self.tasks[run_task].ret
        #print(run_task,"'s terminate time:",terminate_t)
        for ready_task in self.local_rq:
            release_t = (self.tasks[ready_task].prd * self.tasks[ready_task].cnt) + self.tasks[ready_task].off
            #print(ready_task, "'s release time:",release_t)
            if run_task not in self.tasks.keys(): #next task is first task after cpu idle time
                next_evt = release_t
            elif self.prios[run_task] <= self.prios[ready_task]:
                next_evt = max(release_t, terminate_t)
            elif terminate_t <= release_t:
                next_evt = release_t
            else:                        #Occur preemption
                next_evt = max(release_t, self.current_time)
            next_task = ready_task
            next_evt_list.append((next_evt,next_task))
        
        #include running task to next event candidate
        next_evt = (self.tasks[run_task].prd * (self.tasks[run_task].cnt+1)) + self.tasks[run_task].off
        next_task = run_task
        next_evt_list.append((next_evt,next_task))
        
        min_next_evt = min(next_evt_list)
        
        return min_next_evt

    def update_cpu_status(self, next_evt, next_task):
        next_off = next_evt - self.current_time
        if not self.running_task:
            print("There's no running task")
            exit()

        run_task = self.running_task
        if next_task not in self.tasks:
            print("The next task is not in run queue:", next_task)
            exit()
        if next_off < 0:
            print("It seems strange...next offset is negative value", next_off)
            exit()
        
        if next_off < self.tasks[run_task].ret: #Occur preemption
            #print("occur preemption!")
            self.tasks[run_task].ret = self.tasks[run_task].ext - next_off
        else:
            #print("terminate normally")
            calculate_response_time(run_task, self.tasks, self.rtl)
            self.tasks[run_task].ret = self.tasks[run_task].ext
            self.tasks[run_task].cnt = self.tasks[run_task].cnt + 1
        insert_task_in_queue(run_task, self.tasks, self.local_rq)
        next_task = self.local_rq.pop(self.local_rq.index(next_task))
        self.running_task = update_task_status(next_task, next_evt, self.tasks, 'run')

    def print_status(self, command):
        print_cpu_status("cpu status"+command, self.running_task, self.icpu)
        print_task_status("task status"+command, self.tasks)
        print_queue("queue status"+command, self.local_rq)

    def set_priority(self, tasks):
        for name, attr in tasks.items():
            self.prios[name] = attr.prd
            attr.ret = attr.ext