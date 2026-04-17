#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float32


class PathCorrectionNode:
    def __init__(self):
        rospy.init_node('path_correction_node')
        self.pub = rospy.Publisher('/path_correction', Float32, queue_size=10)
        self.rate = rospy.Rate(1)  # 1 Hz
        rospy.loginfo("Path correction node started!")

    def publish_correction(self):
        msg = Float32()
        msg.data = 0.5
        self.pub.publish(msg)
        rospy.loginfo(f"Sent correction: {msg.data}")

    def run(self):
        while not rospy.is_shutdown():
            self.publish_correction()
            self.rate.sleep()


if __name__ == '__main__':
    node = PathCorrectionNode()
    node.run()