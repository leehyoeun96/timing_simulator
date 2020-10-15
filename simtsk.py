from recordtype import recordtype
import time
import copy
from util import *

message = recordtype("message", 'src, id, start, end')
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
        subs_list = []
        subs_list.extend(self.msg_q)
        subs_list.extend(self.ready_msg_q)
        for pred in pred_list:
            if not any(pred in msg.src for msg in subs_list):
                ready_flag = False
        if not len(self.msg_q) == 0:
            self.ready_msg_q.extend(self.msg_q)
            self.msg_q = []
        return ready_flag

    def merge_msg(self, now):
        msg = message(src = [], id = [], start = [], end = 0)
        for recv_msg in self.ready_msg_q:
            for recv_idx, recv_src in enumerate(recv_msg.src):
                if not recv_src in msg.src:
                    msg.src.append(recv_src)
                    msg.start.append(recv_msg.start[recv_idx])
                    msg.id.append(recv_msg.id[recv_idx])
                ##Overwriting message
                elif recv_src in msg.src and recv_msg.start[recv_idx] == max(recv_msg.start[recv_idx], msg.start[recv_idx]):
                    orig_idx = msg.src.index(recv_src)
                    msg.src[orig_idx] = recv_msg.src[recv_idx]
                    msg.start[orig_idx] = recv_msg.start[recv_idx]
                    msg.id[orig_idx] = recv_msg.id[recv_idx]
                #else: print("Received message is out of date.")
        self.ready_msg_q = []
        msg.end = now
        return msg

    def generate_msg(self, now):
        if self.is_src() or len(self.ready_msg_q) == 0:
            print("Source or first task:",self.name)
            msg = self.generate_new_msg(now)
        else:
            print("Sink or intermidiate task:",self.name)
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
        msg = message(src = [self.name], id = [self.msg_id], start = [release_time], end = now)
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
    print_message(taskB.generate_msg())
    for msg in taskC.save_msgs():
        print_message(msg)


Test_Main()
'''