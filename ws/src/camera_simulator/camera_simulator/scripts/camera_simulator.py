#!/usr/bin/env python3
"""
camera_simulator.py
--------------------
Reads frames from a video file (or webcam index) and publishes them
to /usb_cam/image_raw so that opencv_apps face_detection can subscribe
to it — no real camera hardware needed.

Usage:
    rosrun my_robot_tutorials camera_simulator.py
    rosrun my_robot_tutorials camera_simulator.py _video:=/path/to/video.mp4
    rosrun my_robot_tutorials camera_simulator.py _video:=0   (webcam index)
"""

import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import time


class CameraSimulator:
    def __init__(self):
        rospy.init_node('camera_simulator')

        # ── parameters ────────────────────────────────────────────────────────
        # Pass _video:=<path> on rosrun to override, default is webcam 0
        self.video_source = rospy.get_param('~video', 0)
        self.fps          = rospy.get_param('~fps', 15)
        self.topic        = rospy.get_param('~topic', '/usb_cam/image_raw')

        # ── publisher ─────────────────────────────────────────────────────────
        self.pub    = rospy.Publisher(self.topic, Image, queue_size=10)
        self.bridge = CvBridge()
        self.rate   = rospy.Rate(self.fps)

        # ── open video source ─────────────────────────────────────────────────
        # If video_source is a digit string treat it as camera index
        try:
            src = int(self.video_source)
        except (ValueError, TypeError):
            src = self.video_source

        self.cap = cv2.VideoCapture(src)

        if not self.cap.isOpened():
            rospy.logerr(f"Cannot open video source: {self.video_source}")
            rospy.signal_shutdown("Video source not available")
            return

        rospy.loginfo(f"Camera simulator started")
        rospy.loginfo(f"  Source : {self.video_source}")
        rospy.loginfo(f"  Topic  : {self.topic}")
        rospy.loginfo(f"  FPS    : {self.fps}")
        rospy.on_shutdown(self.cleanup)

    def cleanup(self):
        if self.cap.isOpened():
            self.cap.release()
        rospy.loginfo("Camera simulator stopped.")

    def run(self):
        while not rospy.is_shutdown():
            ret, frame = self.cap.read()

            if not ret:
                # End of video file — loop back to start
                rospy.loginfo("End of video — looping back to start.")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # Convert OpenCV frame (BGR) to ROS Image message
            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            msg.header.stamp    = rospy.Time.from_sec(time.time())
            msg.header.frame_id = 'camera'

            self.pub.publish(msg)
            self.rate.sleep()


if __name__ == '__main__':
    try:
        node = CameraSimulator()
        node.run()
    except rospy.ROSInterruptException:
        pass
