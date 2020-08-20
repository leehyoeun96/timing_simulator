from util import *
from simcpu import *
from recordtype import recordtype

task_attr = recordtype("task_attr", 'name, ext, ret, art, prd, cnt, off, aff, rtd, stt')
'''
ext = excution time
ret = remaining excution time
art = latest arrival time
prd = period
cnt = period count
off = offset
aff = affinity
rtd = response time distribution
stt = status
'''

class SIMSYS(object):
    def __init__(self, ncpus, feat_set, cur_time, max_time):
        self.ncpus = ncpus
        self.cpus = [list() for i in range(ncpus)]
        self.global_rq = list()

        self.rtl = list()
        self.prios = dict()
        self.feats = feat_set
        self.current_time = cur_time
        self.max_time = max_time

    def initialize_system(self):
        if not self.feats:
            print("There's no task in task set")
            exit()

        self.create_task_set()        
        self.set_priority()

        for cpu_idx in range(self.ncpus):
            self.cpus[cpu_idx] = SIMCPU(cpu_idx, self.prios, self.tasks, self.current_time, self.max_time)
        
        for attr in self.tasks.values():
            insert_task_in_queue(attr.name, self.tasks, self.global_rq)
        
        ready_task_list = self.allocate_task()
        
        ##initialize CPUs
        for cpu_idx in ready_task_list.keys():
            if cpu_idx >= self.ncpus:
                print("Too few cpus to execute tasks")
                exit()
            print("---------------------------")
            self.cpus[cpu_idx].initialize_cpu(ready_task_list[cpu_idx])
            self.cpus[cpu_idx].print_status(" after initialize")
 
    def allocate_task(self):
        ready_task_list = {}

        while len(self.global_rq):
            ready_task=self.global_rq.pop(0)
            cpu_idx = self.tasks[ready_task].aff
            
            if cpu_idx not in ready_task_list.keys():
                ready_task_list[cpu_idx] = [ready_task]
            else:
                ready_task_list[cpu_idx].append(ready_task)

        return ready_task_list

    def find_min_event_time(self):
        min_event = ()
        if not self.cpus:
            print("There's no running cpu")
            exit()

        for cpu in self.cpus:
            next_event = cpu.find_min_event_time()
            if not next_event: 
                print("There's no running task in CPU", cpu.icpu)
                continue
            if not min_event:
                min_event = next_event
                evt_cpu_idx = cpu.icpu
            elif min_event > next_event: 
                min_event = next_event
                evt_cpu_idx = cpu.icpu

        return evt_cpu_idx, min_event

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
        insert_task_in_queue(run_task, self.tasks, self.global_rq)
        next_task = self.global_rq.pop(self.global_rq.index(next_task))
        self.cpu_running = update_task_status(next_task, next_evt, self.tasks, 'run')

    def create_task_set(self):
        self.tasks = { } 
        for task, features in self.feats.items():
                task_obj = task_attr(task, ext=self.feats[task].ext, ret=0, art=0, prd=self.feats[task].prd, cnt=0, off=self.feats[task].off, aff=self.feats[task].aff, rtd=0, stt='')
                self.tasks.update({task: task_obj})
        print_task_status(" after create task set",self.tasks)
    '''
    def print_status(self, command):
        print_cpu_status("cpu status"+command, self.running_task, self.icpu)
        print_task_status("task status"+command, self.tasks)
        print_queue("queue status"+command, self.local_rq)
    '''
    def set_priority(self):
        for name, attr in self.tasks.items():
            self.prios[name] = attr.prd
            attr.ret = attr.ext