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

        self.gathered_rtl = list()
        self.prios = dict()
        self.feats = feat_set
        self.current_time = cur_time
        self.max_time = max_time

    def initialize_system(self):
        ###
        ##Initialize task set, cpu instance and global queue.
        ###
        if not self.feats:
            print("There's no task in task set")
            exit()

        self.create_task_set()        
        for attr in self.tasks.values():
            insert_task_in_queue(attr.name, self.tasks, self.global_rq)
        self.initialize_cpus()

    def initialize_cpus(self):
        ##initialize CPUs
        for cpu_idx in range(self.ncpus):
            self.cpus[cpu_idx] = SIMCPU(cpu_idx, self.prios, self.tasks, self.current_time, self.max_time)
        self.dispatch_classified_tasks()

        for cpu_idx in range(self.ncpus):
            print("---------------------------")
            self.cpus[cpu_idx].initialize_cpu()
            self.cpus[cpu_idx].print_status(" after initialize")
 
    def dispatch_classified_tasks(self):
        ###
        ##Classify task by it's affinity and dispatch to local run queue
        ###
        classified_tasks = {}

        while len(self.global_rq):
            ready_task=self.global_rq.pop(0)
            cpu_idx = self.tasks[ready_task].aff
            
            if cpu_idx not in classified_tasks.keys():
                classified_tasks[cpu_idx] = [ready_task]
            else:
                classified_tasks[cpu_idx].append(ready_task)        
        
        for affi, tasks in classified_tasks.items():
            if affi >= self.ncpus:
                print("Too few cpus to execute tasks")
                exit()
            for name in tasks:
                insert_task_in_queue(name, self.tasks, self.cpus[affi].local_rq)

    def find_min_event_time(self):
        ###
        ##Find minimum event time among all cpus.
        ###
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

    def update_system_status(self, cpu_idx, next_event):
        ###
        ##Update cpu determined by index with next event time and task.
        ##Also, update global queue and local queue with terminated task.
        ##Finally, update time of system and the cpu.
        ###
        next_time, next_task = next_event
        term_task = self.cpus[cpu_idx].update_cpu_status(next_time, next_task)
        
        insert_task_in_queue(term_task, self.tasks, self.global_rq)
        self.dispatch_classified_tasks()
        
        self.cpus[cpu_idx].current_time = next_time
        self.current_time = next_time
        
        if self.current_time > self.max_time:
            self.gathered_rtl = self.gather_response_time()

    def gather_response_time(self):
        ###
        ##Gather all cpu's response time list.
        ###
        gathered_list = []
        for cpu in self.cpus:
            gathered_list.extend(cpu.rtl)
        return gathered_list

    def create_task_set(self):
        ###
        ##Create task set with task features.
        ###
        self.tasks = { } 
        for task, features in self.feats.items():
                task_obj = task_attr(task, ext=self.feats[task].ext, ret=0, art=0, prd=self.feats[task].prd, cnt=0, off=self.feats[task].off, aff=self.feats[task].aff, rtd=0, stt='')
                self.tasks.update({task: task_obj})
        print_task_status(" after create task set",self.tasks)
        self.set_priority()

    def set_priority(self):
        ###
        ##Prioritize task in task set.
        ###
        for name, attr in self.tasks.items():
            self.prios[name] = attr.prd
            attr.ret = attr.ext