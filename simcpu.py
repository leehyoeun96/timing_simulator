from util import *
from recordtype import recordtype
import random
   
class SIMCPU(object):
    def __init__(self, cpu_idx, prio_set, task_set, lookup_table, cur_time, max_time):
        self.icpu = cpu_idx
        self.running_task = ''
        self.local_rq = list()

        self.rtl = list()
        self.prios = prio_set
        self.tasks = task_set
        self.lut = lookup_table
        self.current_time = cur_time
        self.max_time = max_time

    def initialize_cpu(self):
        ###
        ##Allocate task to cpu in local run queue.
        ###
        if not self.tasks:
            print("Task set is empty")
            exit()
        
        if self.local_rq :
            ready_task=self.local_rq.pop(0)
            arrival_time = self.tasks[ready_task].off
            self.running_task = update_task_status(ready_task, arrival_time, self.tasks, 'run')
            self.current_time = arrival_time
        else : 
            print("CPU", self.icpu, ": Run queue is empty")
            print("You may have assigned more cpu than the task needed.")
            exit()

        return arrival_time

    def find_min_event_time(self):
        ###
        ##Find min event time among tasks in local queue and running task
        ###
        next_evt_list = []
        ##running task must needed
        if not self.running_task:
            print("CPU",self.icpu,": There's no running task")
            return None

        run_task = self.running_task
        terminate_t = self.tasks[run_task].art + self.tasks[run_task].ret
        
        for ready_task in self.local_rq:
            release_t = (self.tasks[ready_task].prd * self.tasks[ready_task].cnt) + self.tasks[ready_task].off
            ##Is it really used?
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
        release_t = (self.tasks[run_task].prd * (self.tasks[run_task].cnt+1)) + self.tasks[run_task].off
        next_task = run_task
        next_evt = max(release_t, terminate_t)
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
            print("CPU", self.icpu, "There's no running task")
            exit()
        if next_task not in self.tasks:
            print("CPU", self.icpu, "The next task is not in task set:", next_task)
            exit()
        if next_off < 0:
            print("CPU", self.icpu, "It seems strange...next offset is negative value", next_off)
            exit()
        
        term_task = self.running_task
        if next_off < self.tasks[term_task].ret: #Occur preemption
            print("occur preemption!")
            self.tasks[term_task].set_ret(self.tasks[term_task].ret - next_off)
        else:
            #print("terminate normally")
            self.tasks[term_task].calculate_response_time(term_task, self.tasks, self.rtl)
            next_ext = self.sampling_ext(term_task)
            self.tasks[term_task].set_ext(next_ext)
            self.tasks[term_task].set_ret(self.tasks[term_task].ext)
            self.tasks[term_task].set_cnt(self.tasks[term_task].cnt + 1)
        '''
        if next_task in self.local_rq:
            self.local_rq.remove(next_task)
        '''
        self.running_task = update_task_status(next_task, next_evt, self.tasks, 'run')
        
        if term_task == next_task:
            #print("Same task as the previous task is running")
            term_task = None
        else:
            self.local_rq.remove(next_task)

        return term_task

    def print_status(self, command):
        ###
        ##Show status of running task, ready task and local run queue
        ###
        print_cpu_status("CPU status "+command, self.running_task, self.icpu)
        print_task_status("Task status "+command, self.tasks)
        print_queue("Queue status "+command, self.local_rq)

    def sampling_ext(self, name):
        ###
        ##Generate real number randomly.
        ##And lookup sampling table.
        ###
        if not name in self.lut:
            print("Define lookup table about", name)
            exit()
        
        ext_sample = 0
        real = random.random()
        cml_prob = 0
        #print(name)
        for time, prob in self.lut[name]:
            cml_prob = cml_prob + prob
            if max(real, cml_prob) != real:
                ext_sample = time
                break
        
        return ext_sample

    def insert_task_in_lrq(self, name):
        if not name in self.tasks.keys():
            print(name, "is not in task_set")
            return
        self.local_rq.append(name)
        update_task_status(name, self.tasks[name].art, self.tasks, 'ready')
        self.local_rq.sort(key=lambda i : self.tasks[i].off + (self.tasks[i].prd * self.tasks[i].cnt))
