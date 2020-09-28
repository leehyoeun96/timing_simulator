from util import *
from simcpu import *
from simtsk import *
from recordtype import recordtype
import random

#task_attr = recordtype("task_attr", 'name, ext, ret, art, prd, cnt, off, aff, rtd, stt')
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
    def __init__(self, ncpus, feat_set, ext_table, task_graph, cur_time, max_time):
        self.ncpus = ncpus
        self.cpus = [list() for i in range(ncpus)]
        self.global_rq = list()

        self.gathered_rtl = list()
        self.gathered_msg = list()
        self.prios = dict()
        self.feats = feat_set
        self.ext_table = ext_table
        self.graph = task_graph
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
        for task in self.tasks.values():
            self.insert_task_in_grq(task.name)
        self.initialize_cpus()

    def initialize_cpus(self):
        ###
        ##Initialize CPUs
        ###
        for cpu_idx in range(self.ncpus):
            self.cpus[cpu_idx] = SIMCPU(cpu_idx, self.prios, self.tasks, self.ext_table, self.graph, self.current_time, self.max_time)
        self.dispatch_classified_tasks()

        for cpu_idx in range(self.ncpus):
            print("---------------------------")
            self.current_time = self.cpus[cpu_idx].initialize_cpu()
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
                self.cpus[affi].insert_task_in_lrq(name)

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
            #print(next_event)
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
        term_task_name = self.cpus[cpu_idx].update_cpu_status(next_time, next_task)
         
        #self.insert_task_in_grq(term_task_name)
        #self.dispatch_classified_tasks()
        self.cpus[cpu_idx].current_time = next_time
        self.current_time = next_time
        if term_task_name == None:
            print("Terminated task is None")
            exit()
            return
        term_task = self.tasks[term_task_name]
        successors = term_task.get_succ()

        for succ_name in successors:
            succ = self.tasks[succ_name]
            msg = term_task.generate_msg(self.current_time)
            print_message("Generate message",msg)
            succ.insert_msg(msg)
            if succ.is_ready():
                self.insert_task_in_grq(succ_name)

        if term_task.is_sink():
            msg = term_task.save_msgs(self.current_time)
            print_message("Generate message",msg)
            self.gathered_msg.append(msg)
        if term_task.is_src:
            self.insert_task_in_grq(term_task_name)

        self.dispatch_classified_tasks()
        print("Current task:",term_task_name)
        print("Successor:",successors)
        input()

        if self.current_time >= self.max_time:
            for cpu in self.cpus:
                #fake event for update cpu status
                cpu.update_cpu_status(self.current_time, cpu.running_task) 
                #cpu.print_status("after final update")
            self.gathered_rtl = self.gather_response_time()
            for msg in self.gathered_msg:
                print_message("Final message", msg)

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
        for task in self.feats.keys():
            ext_sample = self.sampling_ext(task)
            task_obj = SIMTSK(task, ext_sample, self.graph, self.feats, self.current_time)
            #task_obj = task_attr(task, ext=ext_sample, ret=ext_sample, art=0, prd=self.feats[task].prd, cnt=0, off=self.feats[task].off, aff=self.feats[task].aff, rtd=0, stt='')
            self.tasks.update({task: task_obj})
        print_task_status(" after create task set",self.tasks)
        self.set_priority()

    def set_priority(self):
        ###
        ##Prioritize task in task set.
        ###
        for name, task in self.tasks.items():
            self.prios[name] = task.prd

    def sampling_ext(self, name):
        ###
        ##Generate real number randomly.
        ##And lookup sampling table.
        ###
        if not name in self.ext_table:
            print("Define lookup table about", name)
            exit()
        
        ext_sample = 0
        real = random.random()
        cml_prob = 0
        #print(name)
        for time, prob in self.ext_table[name]:
            cml_prob = cml_prob + prob
            if max(real, cml_prob) != real:
                ext_sample = time
                break
        
        if cml_prob > 1 or ext_sample == 0:
            print("total probability is not 1 about", name)
            exit()

        return ext_sample

    def insert_task_in_grq(self, name):
        if not name in self.tasks.keys():
            print(name, "is not in task_set")
            return
        self.global_rq.append(name)
        update_task_status(name, self.tasks[name].art, self.tasks, 'ready')
        self.global_rq.sort(key=lambda i : self.tasks[i].off + (self.tasks[i].prd * self.tasks[i].cnt))
