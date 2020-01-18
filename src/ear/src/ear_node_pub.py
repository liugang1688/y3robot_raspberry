#!/usr/bin/env python
#coding=utf-8
'''ear_node ROS Node'''
# license removed for brevity
import rospy
#import ear
import snowboy_ear as ear
from std_msgs.msg import String



class EarNode():
    def __init__(self):        
        rospy.loginfo("init ear node")
        self.detector = None
        self.pub = rospy.Publisher('ear_listening', String, queue_size=10)
        rospy.init_node('ear_node', anonymous=True)
        self.rate = rospy.Rate(10) # 10hz
    def listen_words(self,words):
        print("ear listend words is :",words)  
        if len(words)>0:
            #rospy.loginfo(words)
            self.pub.publish(words)
            print("ear pub words:",words)
            words = ""
        self.rate.sleep()
    def listening(self):
        ear_listen = ear.Ear()
       # while not rospy.is_shutdown():
        ear_listen.listen(self.listen_words)
        #self.rate.sleep()
        


if __name__ == '__main__':
    try:
        EarNode().listening()
    except rospy.ROSInterruptException:
        raise
