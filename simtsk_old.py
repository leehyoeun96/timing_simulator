from recordtype import recordtype
import time
import copy
from util import *

message = recordtype("message", 'src, id, start, interm, end')
class SIMTSK(object):
    def __init__(self, name, ext, task_graph, task_features):
        ##task attribute
        self.name = name
        self.ext = ext
        self.ret = ext
        self.art = None
        self.prd = task_features[name].prd
        self.cnt = 0 
        self.off = task_features[name].off
        self.aff = task_features[name].aff
        self.rtd = 0
        self.stt = 'wait'
        
        self.msg_q = list()
        self.ready_msg_q = list()
        self.graph = task_graph
        self.feats = task_features
        self.msg_id = 0
    
    def get_pred(self):
        pred =[]
        for key, value in self.graph.items():
            if (key != 'task_0') and (self.name in value) and (self.feats[key].prd == self.prd):
                pred.append(key)
        return pred
        
    def get_succ(self):
        if 'task_0' in self.graph[self.name]:
            return []
        else: return self.graph[self.name]

    def is_src(self):
        flag = False
        if not 'task_0' in self.graph:
            print("Task graph must need key, 'task_0'")
            exit()
        src_list = self.graph['task_0']
        if self.name in src_list:
            flag= True
        return flag
    
    def is_sink(self):
        return self.get_succ() == []

    def is_ready(self):
        pred_list = self.get_pred()
        ready_flag = True
        recv_list = []
        recv_list.extend(self.msg_q)
        recv_list.extend(self.ready_msg_q)
        processed_tasks = []
        end_times = []

        for msg in recv_list:
            processed_tasks.append(msg.src + msg.interm)
            end_times.append(msg.end)
            #print(msg)
            #print("src:",msg.src)
            #print("interm:",msg.interm)
        #print("process task",processed_tasks)
        #print("end", end_times)
        ##1. Task is ready when getting messsage from predecessor which has same period.
        for pred in pred_list:
            if not any(pred in task_list for task_list in processed_tasks):
                ready_flag = False
            else:
                for task_list in processed_tasks:
                    if pred in task_list:
                        msg_end = end_times[processed_tasks.index(task_list)] 
                        '''
                        print("pred task:",pred)
                        print("index:",task_list.index(pred))
                        print("task list, curr task:")
                        print(task_list, self.name)
                        print(msg_end, self.art)
                        '''
                        if not self.art == None and msg_end > self.art:
                            ready_flag = False
                #input()
            '''
            if not any(pred in task for task in processed_tasks):
                ready_flag = False
            '''
            
        ##2. Task is ready when all(?) message arrived before task arrived.
        ##This doesn't work if task is not a source task.
        '''
        if any(self.art < msg.end for msg in recv_list):
            #print(self.art, msg.end)
            ready_flag = False
            #input()
        '''
        if not len(self.msg_q) == 0:
            self.ready_msg_q.extend(self.msg_q)
            self.msg_q = []
        
        #print(self.name, "is ready?:", ready_flag)
        return ready_flag

    def get_dep_msg(self):
        pred_list = self.get_pred()
        dep_msg = []
        print(pred_list, self.ready_msg_q)
        for pred in pred_list:
            for msg in self.ready_msg_q:
                if pred in msg.src or pred in msg.interm:
                    dep_msg.append(msg)
        return dep_msg

    def generate_msg(self, now):
        first_task = True
        #if self.is_src() or len(self.ready_msg_q) == 0:
        dep_msg = self.get_dep_msg()
        print(self.name, dep_msg)
        input()
        if dep_msg: first_task = any(self.art < msg.end for msg in dep_msg)
        if self.is_src() or len(self.ready_msg_q) == 0 or first_task:
            print("Source or first task:",self.name)
            #print("!!!!!!!!!!art < end: ", all(self.art < msg.end for msg in self.ready_msg_q))
            msg = self.generate_new_msg(now)
        else:
            print("Sink or intermidiate task:",self.name)
            msg = self.merge_msg(now)
        #input()
        if any(len(lst) != len(msg.src) for lst in [msg.id, msg.start]):
            print("Wrong message is generated.")
            exit()
        if any(msg.end <= start for start in msg.start):
            print("End",msg.end,"is earlier than start",msg.start)
            exit()
        return msg

    def merge_msg(self, now):
        msg = message(src = [], id = [], start = [], interm=[self.name], end = 0)
        for recv_msg in self.ready_msg_q:
            for recv_idx, recv_src in enumerate(recv_msg.src):
                if not recv_src in msg.src:
                    msg.src.append(recv_src)
                    msg.start.append(recv_msg.start[recv_idx])
                    msg.id.append(recv_msg.id[recv_idx])
                    msg.interm.extend(recv_msg.interm)
                ##Overwriting message
                elif recv_src in msg.src and recv_msg.start[recv_idx] == max(recv_msg.start[recv_idx], msg.start[recv_idx]):
                    orig_idx = msg.src.index(recv_src)
                    msg.src[orig_idx] = recv_msg.src[recv_idx]
                    msg.start[orig_idx] = recv_msg.start[recv_idx]
                    msg.id[orig_idx] = recv_msg.id[recv_idx]
                    msg.interm.extend(recv_msg.interm)
                #else: print("Received message is out of date.")
        self.ready_msg_q = []
        msg.end = now
        return msg

    def generate_new_msg(self, now):
        release_time = (self.prd * self.cnt) + self.off
        msg = message(src=[self.name], id=[self.msg_id], start=[release_time], interm=[], end=now)
        self.msg_id = self.msg_id + 1
        return msg

    def insert_msg(self, msg):
        self.msg_q.append(msg)

    def calculate_response_time(self, response_list):
        release_time = (self.prd * self.cnt) + self.off
        self.rtd = self.art - release_time + self.ret
        print_response_time("Response time", self, release_time)
        
        if self.rtd< 0:
            print("Response time is negative value")
            exit()
        response_list.append(self.rtd)
        return self.rtd
    
    def set_ext(self, new_ext):
        self.ext = new_ext
    def set_ret(self, new_ret):
        self.ret = new_ret
    def set_art(self, new_art):
        self.art = new_art
    def set_cnt(self, new_cnt):
        self.cnt = new_cnt
    def set_stt(self, new_stt):
        self.stt = new_stt

'''
##################
##For Test_Main##
##################
task_feat = recordtype("task_feat", 'ext, prd, off, aff')
feature_set = {
    'task_A': task_feat(ext=10,prd=25, off=0, aff=0),
    'task_B': task_feat(ext=5, prd=25, off=0, aff=0),
    'task_C': task_feat(ext=7, prd=25, off=0, aff=0)
}

task_graph = {
    'task_0': ['task_A', 'task_B'],
    'task_A': ['task_C'],
    'task_B': ['task_C'],
    'task_C': ['task_0']
}

msg1 = message(src = ['task_A', 'task_B', 'task_C'], id = [1,1,1], start = [1,1,1], end = 1 )
msg2 = message(src = ['task_A', 'task_C'], id = [2,2], start = [2,2], end = 1 )
##################

def Test_Main():
    taskB = SIMTSK('task_B', 5, task_graph, feature_set)
    taskC = SIMTSK('task_C', 5, task_graph, feature_set)
    taskB.msg_q = [msg1, msg2]
    taskC.msg_q = [msg1, msg2]
    p = taskC.get_pred()
    print(p)
   
Test_Main()
'''