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
    if response_time< 0:
        print("It seems strange... response time is negative value")
        exit()
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

    def initialize_cpu(self):
        ###
        ##Allocate task to cpu in local run queue.
        ###
        if not self.tasks:
            print("There's no task in task set")
            exit()
        
        if self.local_rq :
            ready_task=self.local_rq.pop(0)
            self.running_task = update_task_status(ready_task, self.current_time, self.tasks, 'run')
        else : print("There's no ready task in run queue")

    def find_min_event_time(self):
        ###
        ##Find min event time among tasks in local queue and running task
        ###
        next_evt_list = []
        if not self.running_task:
            print("There's no running task")
            return None

        run_task = self.running_task
        terminate_t = self.tasks[run_task].art + self.tasks[run_task].ret
        
        for ready_task in self.local_rq:
            release_t = (self.tasks[ready_task].prd * self.tasks[ready_task].cnt) + self.tasks[ready_task].off
            if run_task not in self.tasks.keys():
                next_evt = release_t
            elif self.prios[run_task] <= self.prios[ready_task]:
                next_evt = max(release_t, terminate_t)
            elif terminate_t <= release_t:
                next_evt = release_t
            else: #Occur preemption
                next_evt = max(release_t, self.current_time)
            next_task = ready_task
            next_evt_list.append((next_evt,next_task))
        
        #include running task to next event candidates
        next_evt = (self.tasks[run_task].prd * (self.tasks[run_task].cnt+1)) + self.tasks[run_task].off
        next_task = run_task
        next_evt_list.append((next_evt,next_task))
        
        min_next_evt = min(next_evt_list)
        
        return min_next_evt

    def update_cpu_status(self, next_evt, next_task):
        ###
        ##Update terminate task's time information and status.
        ##And, update next running task's status.
        ###
        next_off = next_evt - self.current_time
        if not self.running_task:
            print("There's no running task")
            exit()
        if next_task not in self.tasks:
            print("The next task is not in run queue:", next_task)
            exit()
        if next_off < 0:
            print("It seems strange...next offset is negative value", next_off)
            exit()
        
        term_task = self.running_task
        if next_off < self.tasks[term_task].ret: #Occur preemption
            #print("occur preemption!")
            self.tasks[term_task].ret = self.tasks[term_task].ret - next_off
        else:
            #print("terminate normally")
            calculate_response_time(term_task, self.tasks, self.rtl)
            self.tasks[term_task].ret = self.tasks[term_task].ext
            self.tasks[term_task].cnt = self.tasks[term_task].cnt + 1
        
        if next_task in self.local_rq:
            self.local_rq.remove(next_task)
        self.running_task = update_task_status(next_task, next_evt, self.tasks, 'run')
        
        if term_task == next_task:
            term_task = None

        return term_task

    def print_status(self, command):
        ###
        ##Show status of running task, ready task and local run queue
        ###
        print_cpu_status("cpu status"+command, self.running_task, self.icpu)
        print_task_status("task status"+command, self.tasks)
        print_queue("queue status"+command, self.local_rq)