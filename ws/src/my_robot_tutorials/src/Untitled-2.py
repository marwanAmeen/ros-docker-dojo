#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class PathCorrectionNode(Node):
    def __init__(self):
        super().__init__('path_correction_node')
        self.pub = self.create_publisher(Float32, '/path_correction', 10)
        self.timer = self.create_timer(1.0, self.publish_correction)
        self.get_logger().info("Path correction node started!")

    def publish_correction(self):
        msg = Float32()
        msg.data = 0.5
        self.pub.publish(msg)
        self.get_logger().info(f"Sent correction: {msg.data}")

def main():
    rclpy.init()
    node = PathCorrectionNode()
    rclpy.spin(node)
    rclpy.shutdown()