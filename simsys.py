from util import *

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
    def __init__(self, cpu_idx, prio_set, task_set, curr_time):
        self.icpu = cpu_idx
        self.cpu_running = ''
        self.rq_ready = list()

        self.rtl = list()
        self.prios = prio_set
        self.tasks = task_set
        self.current_time = curr_time

    def main(self):
        self.initialize_cpu()
        print_cpu_status("cpu status after initialize ", self.cpu_running, self.icpu)
        print_task_status("task status after initialize", self.tasks)
        print_queue("queue after initialize", self.rq_ready)

        while self.current_time < 99:
            print("-------------------------------")
            next_evt, next_task = self.find_min_event_time()
            self.update_system_status(next_evt, next_task)
            
            #print("current system time", curr_t)
            #print("time to next event ", next_evt)
            self.current_time = next_evt
            
            print_cpu_status("cpu status ", self.cpu_running, self.icpu)
            print_task_status("task status ", self.tasks)
            print_queue("queue status", self.rq_ready)
        
        return self.rtl

    def initialize_cpu(self):
        if len(self.tasks) == 0:
            print("There's no task in task set")
            exit()
        for name, attr in self.tasks.items():
            self.prios[name] = attr.prd
            attr.ret = attr.ext
        
        for attr in self.tasks.values():
            insert_task_in_queue(attr.name, self.tasks, self.rq_ready)
        if self.rq_ready : 
            ready_task=self.rq_ready.pop(0)
            self.cpu_running = update_task_status(ready_task, self.current_time, self.tasks, 'run')
        else : print("There's no ready task in run queue")

    def find_min_event_time(self):
        next_evt_list = []
        if not self.rq_ready:
            print("There's no tasks in run queue")
            exit()
        if not self.cpu_running:
            print("There's no running task")
            exit()

        run_task = self.cpu_running
        #print(self.tasks[run_task])
        terminate_t = self.tasks[run_task].art + self.tasks[run_task].ret
        #print(run_task,"'s terminate time:",terminate_t)
        for ready_task in self.rq_ready:
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
        
        #HMMMM.....
        next_evt = (self.tasks[run_task].prd * (self.tasks[run_task].cnt+1)) + self.tasks[run_task].off
        next_task = run_task
        next_evt_list.append((next_evt,next_task))
        
        min_next_evt = min(next_evt_list)
        
        return min_next_evt

    def update_system_status(self, next_evt, next_task):
        next_off = next_evt - self.current_time
        if not self.cpu_running:
            print("There's no running task")
            exit()

        run_task = self.cpu_running
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
        insert_task_in_queue(run_task, self.tasks, self.rq_ready)
        next_task = self.rq_ready.pop(self.rq_ready.index(next_task))
        self.cpu_running = update_task_status(next_task, next_evt, self.tasks, 'run')
