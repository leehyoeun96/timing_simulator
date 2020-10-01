from recordtype import recordtype
import time
import copy
from util import *

message = recordtype("message", 'src, id, start, end')
class SIMTSK(object):
    def __init__(self, name, ext, task_graph, task_features, sys_time):
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
        self.stt = ''
        
        self.msg_q = list()
        self.graph = task_graph
        self.feats = task_features
        self.stand_time = sys_time
        self.is_src = not self.get_pred()
        self.msg_id = 0


    def get_pred(self):
        pred =[]
        for key, value in self.graph.items():
            if (key != 'task_0') and (self.name in value) and (self.feats[key].prd == self.prd):
                pred.append(key)
        return pred

    def get_succ(self):
        if 'task_0' in task_graph[self.name]:
            return []
        else: return task_graph[self.name]

    def is_sink(self):
        return self.get_succ() == []

    def is_ready(self):
        pred_list = self.get_pred()
        #print(self.name,":", pred_list)
        ready_flag = True
        for pred in pred_list:
            #print(pred)
            if not any(pred in msg.src for msg in self.msg_q):
                ready_flag = False

        #print(self.name,"is ready?:", ready_flag)
        return ready_flag

    def merge_msg(self):
        msg = message(src = [], id = [], start = [], end = 0)
        for recv_msg in self.msg_q:
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

        return msg

    def generate_msg(self, curr_time, ret):
        release_time = (self.prd * self.cnt) + self.off
        succ_list = self.get_succ()
        msg = message(src = [], id = [], start = [], end = 0)
        now = curr_time
        now = now + ret
        if self.is_src:
            msg = message(src = [self.name], id = [self.msg_id], start = [release_time], end = now )
            self.msg_id = self.msg_id + 1
            self.stand_time = curr_time
            return msg
        
        msg = self.merge_msg()
        
        length = len(msg.src)
        if any(len(lst) != length for lst in [msg.id, msg.start]):
            print("Wrong message generated.")
            exit()
        if len(self.msg_q) == 0:
            print("Receive 0 message")
            exit()

        msg.end = now
        self.stand_time = now
        return msg

    def save_msgs(self, curr_time, ret):
        if not self.is_sink():
            print("ERROR: This is not sink node")
            exit()
        print("Save messages")
        msg = self.merge_msg()
        self.msg_q = []
        msg.end = curr_time + ret
        return msg
    
    def insert_msg(self, msg):
        self.msg_q.append(msg)

    def calculate_response_time(self, response_list):
        release_time = (self.prd * self.cnt) + self.off
        self.rtd = self.art - release_time + self.ret
        print("*******************************")
        print("task name: ",self.name)
        print("latest arrival time",self.art)
        print("release time", release_time)
        print("remaining excution time", self.ret)
        print("response time", self.rtd)
        print("*******************************")
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
    taskB = SIMTSK('task_B', 5, task_graph, feature_set, time.time())
    taskC = SIMTSK('task_C', 5, task_graph, feature_set, time.time())
    taskB.msg_q = [msg1, msg2]
    taskC.msg_q = [msg1, msg2]
    print_message(taskB.generate_msg())
    for msg in taskC.save_msgs():
        print_message(msg)

#Test_Main()