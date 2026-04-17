#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

rospy.init_node('my_first_node')
pub = rospy.Publisher('/robot_news_radio', String, queue_size=10)
rate = rospy.Rate(1)  # 2 Hz
message_count=0
while not rospy.is_shutdown():
    message_count+=1;
    msg = String()
    msg.data = f"Hi, this is Dan from the Robot News Radio, counter {message_count}"
    pub.publish(msg)
    rate.sleep()