from recordtype import recordtype
import time
import copy
from util import *

message = recordtype("message", 'src, interm, id, start, end')
class SIMTSK(object):
    def __init__(self, name, ext, task_graph, task_features):
        ##task attribute
        self.name = name
        self.ext = ext
        self.ret = ext
        self.art = 0
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

    def is_subgraph_src(self):
        flag = True
        curr_prd = self.prd
        subgraph = {}
        for task, successors in self.graph.items():
            if task == 'task_0': continue
            if self.feats[task].prd == curr_prd:
                subgraph[task] = successors
        if any(self.name in sub for sub in subgraph.values()):
            flag = False

        return flag

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

    def is_first_task(self):
        is_first = False
        return is_first
    
    def is_ready(self):
        pred_list = self.get_pred()
        ready_flag = True
        recv_list = []
        recv_list.extend(self.msg_q)
        recv_list.extend(self.ready_msg_q)
        processed_tasks = []

        for msg in recv_list:
            processed_tasks.extend(msg.src + msg.interm)
        
        ##Task is ready when getting messsage from predecessor which has same period.
        for pred in pred_list:
            if not any(pred in task for task in processed_tasks):
                ready_flag = False

        if not len(self.msg_q) == 0:
            self.ready_msg_q.extend(self.msg_q)
            self.msg_q = []
        return ready_flag

    def merge_msg(self, now):
        msg = message(src = [], id = [], start = [], interm=[self.name], end = 0)
        rcv_msgs = copy.deepcopy(self.ready_msg_q)
        for recv_msg in rcv_msgs:
            if self.art < recv_msg.end: continue
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
            self.ready_msg_q.remove(recv_msg)
        if not msg.src:
            print("ERROR: all received message was not merged")
            exit()
        #self.ready_msg_q = []
        msg.end = now
        return msg
    
    def get_dep_msg(self):
        pred_list = self.get_pred()
        dep_msg = []
        for pred in pred_list:
            for msg in self.ready_msg_q:
                if pred in msg.src or pred in msg.interm:
                    dep_msg.append(msg)
        return dep_msg
    
    def generate_msg(self, now):
        '''
        dep_msg = self.get_dep_msg()
        print(dep_msg)
        if dep_msg: #has data dependency
            first_flag = any(self.art < msg.end for msg in dep_msg)
            if first_flag:
                print(self.name, self.art)
                exit()
        elif self.ready_msg_q: #received message from predecessor
            first_flag = False
        else: first_flag = True
        print(self.name, "is first task?",first_flag)
        '''
        first_flag = all(self.art < msg.end for msg in self.ready_msg_q)

        if self.is_src() or len(self.ready_msg_q) == 0 or first_flag:
            #print("Source or first task of the period:",self.name)
            msg = self.generate_new_msg(now)
        else:
            #print("Sink or intermidiate task:",self.name)
            msg = self.merge_msg(now)
        
        if any(len(lst) != len(msg.src) for lst in [msg.id, msg.start]):
            print("Wrong message is generated.")
            exit()
        if any(msg.end <= start for start in msg.start):
            print("End",msg.end,"is earlier than start",msg.start)
            exit()
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

    def save_msgs(self, now):
        if not self.is_sink():
            print("ERROR: This is not a sink node")
            exit()

        if not len(self.msg_q) == 0:
            msg = self.merge_msg(now)
        else:
            msg = self.generate_new_msg(now)
        if any(msg.end <= start for start in msg.start):
            print("End is earlier than start")
            exit()
        return msg

'''
##################
##For Test_Main##
##################
task_feat = recordtype("task_feat", 'ext, prd, off, aff')
feature_set = {
    'task_A': task_feat(ext=10,prd=5, off=0, aff=0),
    'task_B': task_feat(ext=5, prd=5, off=0, aff=0),
    'task_C': task_feat(ext=7, prd=25, off=10, aff=0),
    'task_D': task_feat(ext=5, prd=25, off=0, aff=0),
    'task_E': task_feat(ext=7, prd=5, off=0, aff=0),
}

task_graph = {
    'task_0': ['task_A', 'task_B'],
    'task_A': ['task_C', 'task_D'],
    'task_B': ['task_E'],
    'task_C': ['task_E'],
    'task_D': ['task_E'],
    'task_E': ['task_0']
}

msg1 = message(src = ['task_A', 'task_B', 'task_C'], interm=[], id = [1,1,1], start = [1,1,1], end = 1 )
msg2 = message(src = ['task_A', 'task_C'], interm=[], id = [2,2], start = [2,2], end = 1 )
##################

def Test_Main():
    taskA = SIMTSK('task_A', 5, task_graph, feature_set)
    taskB = SIMTSK('task_B', 5, task_graph, feature_set)
    taskC = SIMTSK('task_C', 10, task_graph, feature_set)
    taskD = SIMTSK('task_D', 5, task_graph, feature_set)
    taskE = SIMTSK('task_E', 10, task_graph, feature_set)
    
    taskB.msg_q = [msg1, msg2]
    taskC.msg_q = [msg1, msg2]
    #p = taskC.get_pred()
    #p = taskA.is_subgraph_src()
    taskC.merge_msg(0)
    print(p)
   
Test_Main()
'''