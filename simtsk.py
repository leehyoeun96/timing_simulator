from util import *
from simcpu import *
from recordtype import recordtype
import random

class SIMTSK(object):
    def __init__(self, name, ext, prd, off, aff):
        self.msg_q = list()
        ##task attribute
        self.name = name
        self.ext = ext
        self.ret = ext
        self.art = 0
        self.prd = prd
        self.cnt = 0 
        self.off = off
        self.aff = aff
        self.rtd = 0
        self.stt = ''

    def initialize_task(self):
        print("")
    
    def calculate_response_time(self, task, tasks, response_list):
        release_time = (self.prd * self.cnt) + self.off
        response_time = self.art - release_time + self.ret
        print("*******************************")
        print("task name: ",self.name)
        print("latest arrival time",self.art)
        print("release time", release_time)
        print("remainig excution time", self.ret)
        print("response time", response_time)
        print("*******************************")
        if response_time< 0:
            print("It seems strange... response time is negative value")
            exit()
        response_list.append(response_time)
        return response_list
    
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