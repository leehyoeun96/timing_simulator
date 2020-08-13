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

    def __init__(self, prio_set, task_set, ncpus):
        self.cpus = [0 for x in range(ncpus)]
        self.rq = [list() for x in range(ncpus)]
        self.rtl = list()
        self.prios = prio_set
        self.tasks = task_set
        self.ncpus = ncpus
        self.current_time = 0
        self.affi = self.ncpus - 1

    def main(self):
        self.initialize_system()
        print_cpu_status("cpu status after initialize ", self.cpus)
        print_task_status("task status after initialize", self.tasks)
        print_queue("queue after initialize", self.rq[self.affi])

        while self.current_time < 99:
            print("-------------------------------")
            next_evt, next_task = self.find_min_event_time()
            self.update_system_status(next_evt, next_task)
            
            #print("current system time", curr_t)
            #print("time to next event ", next_evt)
            self.current_time = next_evt
            
            print_cpu_status("cpu status ", self.cpus)
            print_task_status("task status ", self.tasks)
            print_queue("queue status", self.rq[self.affi])
            #input('').split(" ")[-1]
        
        return self.rtl

    def initialize_system(self):
        if len(self.tasks) == 0:
            print("There's no task in task set")
            exit()
        for name, attr in self.tasks.items():
            self.prios[name] = attr.prd
            attr.ret = attr.ext
        
        #for self.affi in range(len(self.cpus)):
        for attr in self.tasks.values():
            insert_task_in_queue(attr.name, self.affi, self.tasks, self.rq)
        if self.rq[self.affi] : 
            ready_task=self.rq[self.affi].pop(0)
            assign_task_to_cpu(ready_task, self.current_time, self.affi, self.tasks, self.cpus)
        else : print("There's no ready task in run queue")

    def find_min_event_time(self):
        next_evt_list = []
        if not self.rq[self.affi]:
            print("There's no tasks in run queue")
            exit()
        
        run_task = self.cpus[self.affi]
        #print(self.tasks[run_task])
        terminate_t = self.tasks[run_task].art + self.tasks[run_task].ret
        #print(run_task,"'s terminate time:",terminate_t)
        for ready_task in self.rq[self.affi]:
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
        run_task = self.cpus[self.affi]

        #if next_task not in self.rq[self.affi]:
        if next_task not in self.tasks:
            print("The next task is not in run self.rq:", next_task)
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
        insert_task_in_queue(run_task, self.affi, self.tasks, self.rq)
        next_task = self.rq[self.affi].pop(self.rq[self.affi].index(next_task))
        assign_task_to_cpu(next_task, next_evt, self.affi, self.tasks, self.cpus)
