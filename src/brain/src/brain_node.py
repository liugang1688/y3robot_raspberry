#!/usr/bin/env python
#coding=utf-8
'''barin_node ROS Node'''
# license removed for brevity

import os,sys
import rospy
from std_msgs.msg import String



APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir))
sys.path.append(os.path.join(APP_PATH,"sdk/"))
sys.path.append(os.path.join(APP_PATH,"util/"))
sys.path.append(os.path.join(APP_PATH,"robot_msg/"))

from robot_msg.msg import BrainCmd

try:    
    import baidu_unit
    import config_helper
    from utils import *
except ImportError:
    raise


import sys
reload(sys)
sys.setdefaultencoding('utf8')


class Brain():
    def __init__(self):
        self.is_wakeup = True #是否被唤醒
        #self.name = "豆豆,兜兜,斗斗,嘟嘟,都督,读读,肚肚,毒毒,独独,杜杜"
        self._nlu = baidu_unit.BaiDuUnit()
        rospy.Subscriber("ear_listening", String, self.listening_callback)
        self._say_pub = rospy.Publisher('brain_say', BrainCmd, queue_size=10)               
        rospy.init_node('brain_node', anonymous=True)
        self._say_rate = rospy.Rate(10)       
    
    def listening_callback(self,data):
        print("brain recive ear listen words:",data.data)
        #self.say(data.data)
        self.converstation(data.data)

    def sing(self,audio_path):        
        bv_msg = BrainCmd()

        bv_msg.cmd_by = BrainCmd.MOUTH
        bv_msg.cmd_type = 2 
        bv_msg.msg = audio_path
        bv_msg.priority = BrainCmd.NORMAL
        self._say_pub.publish(bv_msg)

    def sing_bycmd(self,cmd_type,cmd):  
        '''
        cmd_type 0: say words
        cmd_type 1: play audio by commond,explain commond and play audio
        cmd_type 2: play audio by with filepath
        cmd_type 10: play music by name
        '''      
        bv_msg = BrainCmd()

        bv_msg.cmd_by = BrainCmd.MOUTH
        bv_msg.cmd_type = cmd_type 
        bv_msg.msg = cmd
        bv_msg.priority = BrainCmd.NORMAL
        self._say_pub.publish(bv_msg)

    def say(self,msg,is_ending_saying=False):
        rospy.loginfo(msg)
        bv_msg = BrainCmd()

        bv_msg.cmd_by = BrainCmd.MOUTH
        bv_msg.cmd_type = 0 
        bv_msg.msg = msg        
        bv_msg.priority = BrainCmd.NORMAL if is_ending_saying == False else BrainCmd.HIGH
        self._say_pub.publish(bv_msg)

    def converstation(self,heard_voice):
        #///TODO:1.说的时候不能听，2.不能连续对话；/
        # 3判断无法识别的对话并记录，mongdb数据库保存
        # 4 对话人鉴权，确定是什么身份，认识的人（家人（性别，年龄），朋友），陌生人
        print("heard_voice:",heard_voice)
        if heard_voice == "ear_status:0":
            self.say("进入休眠状态，您需要重新唤醒")
            return True
        if (self.is_wakeup and len(heard_voice)>0):  # 如果被唤醒了，执行指令
            stop_words = ('别讲','安静', '别说', '不要讲', '不要说', '不要再说')
            #self.say(heard_voice)
            if len(list(x for x in stop_words if x in heard_voice)) > 0:
                self.say("好的，听你说",True)
            else:
                parsed = self._nlu.getUnit(heard_voice)
                intent = self._nlu.getIntent(parsed)
                if len(intent)==0:
                    #如果意图为空，则记录到数据库中，并更改答复文字
                    #self._dbAccess.insert_one("entry",{"voice":heard_voice,"unitResult":parsed,"date":time.strftime("%Y-%m-%d", time.localtime())})
                    self.say("我还是小宝宝，你说的这么难，我都不理解")
                elif intent == "MUSICINFO":
                    user_music_name  = self._nlu.getSlotWords(parsed,"MUSICINFO","user_music_name")
                    print("user_music_name-->",user_music_name)
                    self.say(self._nlu.getSay(parsed))
                    self.sing_bycmd(10,user_music_name[0])
                else:
                    self.say(self._nlu.getSay(parsed))
        elif self._check_voice_has_name(heard_voice):  # 如果叫了名字，则唤醒
            self.is_wakeup = True
            # self._ear.record_seconds = 5  # 唤醒成功后将每次听的时长更新为5S
            self.say("睡一觉起来真好")
        elif (not self.is_wakeup):  # 如果没被唤醒什么都不做，等待唤醒
            self.say("请说：你好，嘟嘟 唤醒我.")
        else:
            print("什么也没说")
    def _check_voice_has_name(self,txt_voice):
        result = False
        name_list = self.name.split(',')
        num = len(name_list)
        for i in range(num):
            if name_list[i] in txt_voice:
                result = True
                break
        return  result   


    
    def start_work(self):        
        #self.sing_bycmd(1,"TURN_ON")
        self.say("嘟嘟启动成功，等待唤醒。")
        rospy.spin()


if __name__ == '__main__':
    try:
        brain = Brain()
        brain.start_work()  
    except BaseException:
        raise
