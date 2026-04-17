#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float32


class MotionPlanningNode:
    def __init__(self):
        rospy.init_node('motion_planning_node')
        self.sub = rospy.Subscriber('/path_correction', Float32, self.callback)
        rospy.loginfo("Motion planning node waiting for corrections...")

    def callback(self, msg):
        rospy.loginfo(f"Received correction: {msg.data} — adjusting path!")

    def run(self):
        rospy.spin()


if __name__ == '__main__':
    node = MotionPlanningNode()
    node.run()