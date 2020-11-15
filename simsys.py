from util import *
from simcpu import *
from simtsk import *
import math

class SIMSYS(object):
    def __init__(self, feat_set, ext_table, task_graph, max_time):
        self.global_rq = list()

        self.gathered_rtl = list()
        self.gathered_msg = list()
        self.prios = dict()
        self.feats = feat_set
        self.ext_table = ext_table
        self.graph = task_graph
        self.current_time = 0
        self.max_time = max_time

        self.total_prod = {name: 0 for name in self.feats}
        self.total_prod_time = 0

    def initialize_system(self):
        ###
        ##Initialize task set, cpu instance and global queue.
        ###
        if not self.feats:
            print("There's no task in task set")
            exit()

        self.create_task_set()   
        self.set_cpu_number()

        for task in self.tasks.values():
            if task.is_ready():
                self.insert_task_in_grq(task.name)
        
        self.initialize_cpus()

    def initialize_cpus(self):
        ###
        ##Initialize CPUs
        ###
        time_list = []
        for cpu_idx in range(self.ncpus):
            self.cpus[cpu_idx] = SIMCPU(cpu_idx, self.prios, self.tasks, self.ext_table, self.graph, self.max_time)
        self.dispatch_classified_tasks()

        for cpu_idx in range(self.ncpus):
            print("........................")
            #self.current_time = self.cpus[cpu_idx].initialize_cpu()
            #time_list.append(self.cpus[cpu_idx].initialize_cpu())
            self.cpus[cpu_idx].print_status("after initialize")

        #   self.current_time = min(time_list)
    
    def insert_evt(self, evts, k, v):
        if k in evts.keys():
            evts[k].append(v)
        else:
            evts[k] = [v]

    def find_min_event_time(self):
        ###
        ##Find minimum event time among all cpus.
        ###
        # min_event = ()
        min_time = math.inf #infinite number
        min_tasks = []
        evt_cpu = []
        if not self.cpus:
            print("There's no running cpu")
            exit()
        
        for cpu in self.cpus:
            term_flag, term_task_name = cpu.is_terminated()
            if term_flag: self.insert_ready_successors(term_task_name)
            next_evt = cpu.find_min_event_time()

            if not next_evt:
                #print("There's no running task in CPU", cpu.icpu)
                continue
            next_time, next_task = next_evt
            if min_time == next_time:
                min_time = next_time
                min_tasks.append(next_task)
                evt_cpu.append(cpu.icpu)
            elif min_time > next_time:
                min_tasks.clear()
                evt_cpu.clear()
                min_time = next_time
                min_tasks.append(next_task)
                evt_cpu.append(cpu.icpu)
        
        if not len(evt_cpu):
            print("There's no event.. It seems strange.")
            exit()
        return evt_cpu, min_time, min_tasks

    def update_system_status(self, cpu_list, next_time, next_tasks):
        ###
        ##Update cpu determined by index with next event time and task.
        ##Also, update global queue and local queue with terminated task.
        ##Finally, update time of system and the cpu.
        ###
        #next_time, next_task = next_event
        for task_idx, cpu_idx in enumerate(cpu_list):
            next_task = next_tasks[task_idx]
            #print("PLZ....",cpu_idx, next_task, next_time)
            term_task_name, check_param = self.cpus[cpu_idx].update_cpu_status(next_time, next_task)
            if term_task_name:
                print("????",term_task_name, next_task)
                self.check_total_time(term_task_name, check_param, next_time)
                running_same_task = term_task_name == next_task
                #if self.tasks[term_task_name].is_src(): self.insert_task_in_grq(term_task_name)
                if self.tasks[term_task_name].is_src() and not running_same_task: self.insert_task_in_grq(term_task_name)
                self.dispatch_classified_tasks()

        self.current_time = next_time

        if self.current_time >= self.max_time:
            for cpu in self.cpus:
                #fake event for update cpu status
                cpu.update_cpu_status(self.current_time, cpu.running_task) 
            self.gathered_rtl = self.gather_response_time()

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

    def insert_ready_successors(self, term_task_name):
        ###
        ## if term_task is not None, it send messages to successors
        ## And insert successors to ready queue, if it is ready. 
        ###
        if not term_task_name:
            return

        self.process_message(term_task_name)

        term_task = self.tasks[term_task_name]
        terminate_t = term_task.art + term_task.ret
        successors = term_task.get_succ()
        for succ_name in successors:
            succ = self.tasks[succ_name]
            is_redundant_task = self.cpus[succ.aff].running_task == succ_name or succ_name in self.cpus[succ.aff].local_rq #?
            if succ.is_ready() and not is_redundant_task: #?
                self.insert_task_in_grq(succ_name)
        
        self.dispatch_classified_tasks()
 
    def process_message(self, term_task_name):
        term_task = self.tasks[term_task_name]
        successors = term_task.get_succ()
        msg = term_task.generate_msg(self.current_time + term_task.ret)
        print_message(msg)

        for succ_name in successors:
            succ = self.tasks[succ_name]
            succ.insert_msg(msg)

        if term_task.is_sink():
            self.gathered_msg.append(msg)

    def gather_response_time(self):
        ###
        ##Gather all cpu's response time list.
        ##Return task_list for debugging
        ###
        task_list = {name: [] for name in self.tasks}
        total_list = []
        for cpu in self.cpus:
            total_list.extend(cpu.cpu_rtl)
            for task, list in cpu.task_rtl.items():
                if not list == []:
                    task_list[task] = list

        return total_list#, task_list

    def create_task_set(self):
        ###
        ##Create task set with task features.
        ###
        self.tasks = { } 
        for task in self.feats.keys():
            ext_sample = sampling_ext(self.ext_table, task)
            task_obj = SIMTSK(task, ext_sample, self.graph, self.feats)
            self.tasks.update({task: task_obj})
        print_task_status(" after create task set",self.tasks)
        self.set_priority()

    def set_cpu_number(self):
        max_affinity = 0
        for t in self.tasks.values():
            if t.aff > max_affinity:
                max_affinity = t.aff
        self.ncpus = max_affinity + 1
        self.cpus = [list() for i in range(self.ncpus)]

    def set_priority(self):
        ###
        ##Prioritize task in task set.
        ###
        for name, task in self.tasks.items():
            self.prios[name] = task.prd

    def insert_task_in_grq(self, name):
        if not name in self.tasks.keys():
            print(name, "is not in task_set")
            return
        self.global_rq.append(name)
        update_task_status(name, self.tasks[name].art, self.tasks, 'ready')
        self.global_rq.sort(key=lambda i : self.tasks[i].off + (self.tasks[i].prd * self.tasks[i].cnt))

    def check_total_time(self, name, param, next_t):
        ###
        ##Compare task's total produced time and consumed time.
        ###
        cons_time, prod_time = param
        #curr_prod = min(next_t - self.current_time, capture_ret)
        '''
        print("current produced time:", prod_time)
        print("next - curr:", next_t - self.current_time)
        print("next:", next_t)
        print("curr:", self.current_time)
        #print("ret:", capture_ret)
        '''
        self.total_prod[name] = self.total_prod[name] + prod_time
        if not self.total_prod[name] == cons_time:
            print("Total produced", self.total_prod[name], ",Total comsumed:",cons_time,":", name)
            exit()