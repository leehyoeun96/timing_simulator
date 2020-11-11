from util import *
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

    def find_min_event_time(self):
        ###
        ##Find min event time among tasks in local queue and running task
        ###
        next_evt_list = []
        next_evts = {}
        run_task_name = self.running_task
        
        if not run_task_name and not len(self.local_rq):
            print("No running task, No ready task")
            task = None
            next_t = self.current_time
            next_evt_list.append((next_t,task))
            #self.insert_evt(next_evts, next_t, task)
        elif not run_task_name and len(self.local_rq):
            print("No running task")
            #task = self.local_rq.pop(0)
            task = self.local_rq[0]
            release_t = (self.tasks[task].prd * self.tasks[task].cnt) + self.tasks[task].off
            next_evt_list.append((release_t,task))
            #self.insert_evt(next_evts, release_t, task)
        else:
            print("Running task exist.")
            run_task = self.tasks[run_task_name]
            terminate_t = run_task.art + run_task.ret
            for ready_task in self.local_rq:
                if run_task_name == ready_task:
                    print("ERROR: Same task as running task is in ready queue.:", ready_task)
                    exit()
                release_t = (self.tasks[ready_task].prd * self.tasks[ready_task].cnt) + self.tasks[ready_task].off
                if self.prios[run_task_name] <= self.prios[ready_task]:
                    next_evt = max(release_t, terminate_t)
                elif terminate_t <= release_t:
                    next_evt = release_t
                else: #Occur preemption
                    next_evt = max(release_t, self.current_time)
                next_task = ready_task
                next_evt_list.append((next_evt,next_task))
                #self.insert_evt(next_evts, next_evt, next_task)
            
            #include running task to next event candidates
            if run_task.is_ready():
                release_t = (run_task.prd * (run_task.cnt+1)) + run_task.off
                next_evt = max(release_t, terminate_t)
                next_evt_list.append((next_evt,run_task_name))
                #self.insert_evt(next_evts, next_evt, run_task_name)
            print(run_task_name)

        if len(next_evt_list) == 0:
            print("There's no next event")
            task = None
            next_t = self.current_time ##??
            min_evt = (next_t, task)
            #self.insert_evt(next_evts, next_t, task)
        else: min_evt = min(next_evt_list)
        '''
        min_time = min(next_evts.keys())
        min_task = next_evts[min_time]
        '''
        return min_evt

    def find_min_event_time1(self):
        ###
        ##Find min event time among tasks in local queue and running task
        ###
        next_evt_list = []
        
        ##running task must needed
        run_task = self.running_task
        
        if not run_task:
            if not len(self.local_rq):
                print("ERROR: Too many CPUs than tasks needed.")
                exit()
            #print("CPU",self.icpu,": There's no running task")
            first_task=self.local_rq[0]
            release_t = self.tasks[first_task].off
            return (release_t, first_task)
        
        terminate_t = self.tasks[run_task].art + self.tasks[run_task].ret
        for ready_task in self.local_rq:
            release_t = (self.tasks[ready_task].prd * self.tasks[ready_task].cnt) + self.tasks[ready_task].off
            ##Is it really used?
            if run_task not in self.tasks.keys():
                next_evt = release_t
            elif self.prios[run_task] <= self.prios[ready_task] and not run_task == ready_task:
                next_evt = max(release_t, terminate_t)
            elif terminate_t <= release_t:
                next_evt = release_t
            else: #Occur preemption
                next_evt = max(release_t, self.current_time)
            next_task = ready_task
            next_evt_list.append((next_evt,next_task))
        #include running task to next event candidates
        if self.tasks[run_task].is_ready():
            release_t = (self.tasks[run_task].prd * (self.tasks[run_task].cnt+1)) + self.tasks[run_task].off
            next_task = run_task
            next_evt = max(release_t, terminate_t)
            next_evt_list.append((next_evt,next_task))
        #print(run_task, "'s event list:",next_evt_list)
        print(run_task)
        min_next_evt = min(next_evt_list)

        return min_next_evt

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
            else:
                #print("Terminate normally")
                self.total_cons[term_task_name] = self.total_cons[term_task_name] + term_task.ret

                self.cpu_rtl.append(term_task.calculate_response_time(self.task_rtl[term_task_name]))
                next_ext = sampling_ext(self.ext_table, term_task_name)
                term_task.set_ext(next_ext)
                term_task.set_ret(term_task.ext)
                term_task.set_cnt(term_task.cnt + 1)
            
            update_task_status(term_task_name, term_task.art, self.tasks, 'wait')

            check_param  = (self.total_cons[term_task_name], saved_ret)
        
        if next_task in self.local_rq:
            self.local_rq.remove(next_task)
        if next_task in self.tasks:
            print("CPU", self.icpu, "The next task", next_task, " is in task set")
            self.running_task = update_task_status(next_task, next_evt, self.tasks, 'run')

        self.current_time = next_evt
        
        #print("Next task:", self.running_task)
        #print("Term task:", term_task_name)
        return term_task_name, check_param

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
