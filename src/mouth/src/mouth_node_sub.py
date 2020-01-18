#!/usr/bin/env python
'''mouth_node ROS Node'''

import mouth
from std_msgs.msg import String

import os,sys
import rospy


APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir))
sys.path.append(os.path.join(APP_PATH,"robot_msg/"))
sys.path.append(os.path.join(APP_PATH,"util/"))

import config_helper
from robot_msg.msg import BrainCmd


mouth_instance = mouth.Mouth()
def callback(args):
    '''mouth_node Callback Function'''
    if args.cmd_by == BrainCmd.MOUTH:
        rospy.loginfo(rospy.get_caller_id() + "I heard %s", args.msg)

        if args.cmd_type == 0:   #say 
            mouth_instance.say(args.msg,True,True if args.priority == 1 else False)
        elif args.cmd_type ==1 and len(args.msg) >0:#if play audio by commond,explain commond and play audio
            if args.msg == "TURN_ON": #start commputer play audio
                full_path = os.path.join(APP_PATH,config_helper.config.START_AUDIO)            
                mouth_instance.playAudio(full_path)
        elif args.cmd_type ==2 and len(args.msg) >0:#play input audio path,msg meas audio path
            mouth_instance.playAudio(args.msg)
        elif args.cmd_type ==10 and len(args.msg) >0:
            mouth_instance.play_music(args.msg)
        else:
            pass


def listener():
    '''mouth_node Subscriber'''
    # In ROS, nodes are uniquely named. If two nodes with the same
    # node are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('mouth_node', anonymous=True)
    rospy.Subscriber("brain_say", BrainCmd, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':   
    listener()
        
