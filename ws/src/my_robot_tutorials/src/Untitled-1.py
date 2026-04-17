#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class MotionPlanningNode(Node):
    def __init__(self):
        super().__init__('motion_planning_node')
        self.sub = self.create_subscription(
            Float32, '/path_correction', self.callback, 10)
        self.get_logger().info("Motion planning node waiting for corrections...")

    def callback(self, msg):
        self.get_logger().info(f"Received correction: {msg.data} — adjusting path!")

def main():
    rclpy.init()
    node = MotionPlanningNode()
    rclpy.spin(node)
    rclpy.shutdown()