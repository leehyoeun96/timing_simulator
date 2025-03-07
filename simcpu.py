from simutil import *
import random
import math
   
class SIMCPU(object):
    def __init__(self, cpu_idx, prio_set, task_set, ext_table, task_graph, max_time):
        self.icpu = cpu_idx
        self.running_task = ''
        self.local_rq = list()

        self.cpu_rtl = list()
        self.prios = prio_set
        self.tasks = task_set
        self.ext_table = ext_table
        self.graph = task_graph
        self.current_time = 0
        self.max_time = max_time
        self.prio_term_task = None

        self.total_cons = {name: 0 for name in self.tasks}
        self.total_prod = {name: 0 for name in self.tasks}
        self.task_rtl = {name: [] for name in self.tasks}

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
        '''
        else : 
            print("CPU", self.icpu, ": Run queue is empty")
            print("You may have assigned more cpu than the task needed.")
            exit()
        '''
        return self.current_time

    def insert_evt(self, evts, k, v):
        if k in evts.keys():
            evts[k].append(v)
        else:
            evts[k] = [v]

    def max_pred_term_time(self, ready_task):
        ###
        ##Get maximum time between termination time of predecessors.
        ##Return 0, if there's no predecessor for the same period.
        ###
        pred_list = ready_task.get_pred()
        term_time_list = []
        term_t = 0
        for pred in pred_list:
            term_time_list.append(self.tasks[pred].art + self.tasks[pred].ret)
        if term_time_list: term_t = max(term_time_list)
        return term_t

    def find_min_event_time(self):
        ###
        ##Find min event time among tasks in local queue and running task
        ###
        next_evt_list = []
        next_evts = {}
        run_task_name = self.running_task
 
        if not run_task_name and not len(self.local_rq):
            #print("No running task, No ready task")
            task = None
            #next_t = self.current_time #?
            next_t = math.inf #?
            next_evt_list.append((next_t,task))
        elif not run_task_name and len(self.local_rq):
            #print("No running task")
            ready_task_name = self.local_rq[0]
            ready_task = self.tasks[ready_task_name]
            release_t = (ready_task.prd * ready_task.cnt) + ready_task.off
            pred_term_t = self.max_pred_term_time(ready_task)
            evt_t = max(release_t,pred_term_t)
            next_evt_list.append((evt_t,ready_task_name))
        else:
            #print("Running task exist.")
            run_task = self.tasks[run_task_name]
            terminate_t = run_task.art + run_task.ret
            for ready_task_name in self.local_rq:
                if run_task_name == ready_task_name:
                    print("ERROR: Same task as running task is in ready queue.:", ready_task_name)
                    exit()
                ready_task = self.tasks[ready_task_name]
                release_t = (ready_task.prd * ready_task.cnt) + ready_task.off
                pred_term_t = self.max_pred_term_time(ready_task)
                if self.prios[run_task_name] <= self.prios[ready_task_name]:
                    next_evt = max(release_t, terminate_t, pred_term_t)
                elif terminate_t <= release_t:
                    next_evt = max(release_t, pred_term_t)
                else: #Occur preemption
                    next_evt = max(release_t, self.current_time, pred_term_t)
                next_evt_list.append((next_evt,ready_task_name))
            
            #include running task to next event candidates
            if run_task.is_ready():
                pred_term_t = self.max_pred_term_time(run_task)
                release_t = (run_task.prd * (run_task.cnt+1)) + run_task.off
                next_evt = max(release_t, terminate_t, pred_term_t)
                next_evt_list.append((next_evt,run_task_name))

        if len(next_evt_list) == 0:
            #print("There's no next event: CPU",self.icpu)
            task = None
            #next_t = self.current_time #?
            next_t = math.inf #?
            min_evt = (next_t, task)
            #exit()
        else: min_evt = min(next_evt_list)
        '''
        min_time = min(next_evts.keys())
        min_task = next_evts[min_time]
        '''
        return min_evt
    
    def update_cpu_status(self, next_evt, next_task):
        ###
        ##Update terminate task's time information and status.
        ##And, update next running task's status.
        ###
        next_off = next_evt - self.current_time
        
        if next_off < 0:
            print("CPU", self.icpu, "Next offset " , next_off, "is negative value")
            exit()
        
        term_task_name = None
        check_param = ()
        
        if self.running_task:
            term_task_name = self.running_task
            term_task = self.tasks[term_task_name]
            saved_ret = term_task.ret
            if next_off < term_task.ret: #Occur preemption
                #print("Occur preemption!")
                self.total_cons[term_task_name] = self.total_cons[term_task_name] + next_off
                term_task.set_ret(term_task.ret - next_off)
                prod_time = term_task.ext - term_task.ret
            else:
                #print("Terminate normally")
                self.total_cons[term_task_name] = self.total_cons[term_task_name] + term_task.ret

                self.cpu_rtl.append(term_task.calculate_response_time(self.task_rtl[term_task_name]))
                next_ext = sampling_ext(self.ext_table, term_task_name)
                term_task.set_ext(next_ext)
                term_task.set_ret(term_task.ext)
                term_task.set_cnt(term_task.cnt + 1)
                prod_time = term_task.ext
            
            update_task_status(term_task_name, term_task.art, self.tasks, 'wait')

            #check_param  = (self.total_cons[term_task_name], prod_time)
            self.check_cpu_time(term_task_name, saved_ret, next_evt);
        if next_task in self.local_rq:
            self.local_rq.remove(next_task)
        if next_task in self.tasks:
            #print("CPU", self.icpu, ":The next task", next_task, " is in task set")
            self.running_task = update_task_status(next_task, next_evt, self.tasks, 'run')
        self.current_time = next_evt
        
        #print("Next task:", self.running_task)
        #print("Term task:", term_task_name)
        return term_task_name
   
    def check_cpu_time(self, name, ret, next_t):
        ###
        ##Compare task's total produced time and consumed time.
        ###
        #cons_time, prod_time = param
        cons_time = self.total_cons[name] ##Consumed time by task
        prod_time = min(next_t - self.current_time, ret) ##Produced time by CPU
        '''
        print("current produced time:", prod_time)
        print("next - curr:", next_t - self.current_time)
        print("next:", next_t)
        print("curr:", self.current_time)
        print("ret:", ret)
        '''
        self.total_prod[name] = self.total_prod[name] + prod_time
        if not self.total_prod[name] == cons_time:
            print("Total produced", self.total_prod[name], ",Total comsumed:",cons_time,":", name)
            exit()

    def is_terminated(self):
        ###
        ## If running task is terminated or there's no running task,
        ## returns term_flag True.
        ###
        run_task = self.running_task
        term_flag = True
        same_task_flag = False
        task_cnt = -1
        curr_term_task = ()
        
        ##To prevent same task termination repeatedly. 11/7
        if run_task: task_cnt = self.tasks[run_task].cnt
        curr_term_task = (run_task, task_cnt)
        if self.prio_term_task: 
            same_task_flag = curr_term_task == self.prio_term_task
        if same_task_flag:
            term_flag = False
            run_task = None
            return term_flag, run_task

        ##running task must need
        if not run_task:
            #print("CPU",self.icpu,": There's no running task")
            term_flag = False
            return term_flag, run_task

        terminate_t = self.tasks[run_task].art + self.tasks[run_task].ret
        for ready_task in self.local_rq:
            release_t = (self.tasks[ready_task].prd * self.tasks[ready_task].cnt) + self.tasks[ready_task].off
            if not(self.prios[run_task] <= self.prios[ready_task] or terminate_t <= release_t):
                term_flag = False
        
        self.prio_term_task = curr_term_task
        #print(run_task, "is terminated?:", term_flag)
        return term_flag, run_task

    def print_status(self, command):
        ###
        ##Show status of running task, ready task and local run queue
        ###
        print_cpu_status("CPU status "+command, self.running_task, self.icpu)
        print_task_status("Task status "+command, self.tasks)
        print_queue("Queue status "+command, self.local_rq)

    def insert_task_in_lrq(self, name):
        if not name in self.tasks.keys():
            print(name, "is not in task_set")
            return
        self.local_rq.append(name)
        update_task_status(name, self.tasks[name].art, self.tasks, 'ready')
        self.local_rq.sort(key=lambda i : self.tasks[i].off + (self.tasks[i].prd * self.tasks[i].cnt))
