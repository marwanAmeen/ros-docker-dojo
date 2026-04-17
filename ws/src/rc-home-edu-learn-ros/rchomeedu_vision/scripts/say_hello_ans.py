#!/usr/bin/env python3

import rospy
from sound_play.libsoundplay import SoundClient
from opencv_apps.msg import FaceArrayStamped

greet_flag = 0

class SayHello:
    def __init__(self):
        rospy.init_node('say_hello')
        rospy.on_shutdown(self.cleanup)

        rospy.loginfo("=" * 50)
        rospy.loginfo("  SayHello Node Starting...")
        rospy.loginfo("=" * 50)

        # Create the sound client object
        rospy.loginfo("Connecting to soundplay server...")
        self.soundhandle = SoundClient()

        # Wait for sound server to connect
        rospy.sleep(1)
        self.soundhandle.stopAll()
        rospy.loginfo("Sound client connected and ready.")

        # Subscribe to face detection
        rospy.loginfo("Subscribing to /face_detection/faces ...")
        rospy.Subscriber('/face_detection/faces', FaceArrayStamped, self.talkback)

        rospy.loginfo("=" * 50)
        rospy.loginfo("  Ready — waiting for faces...")
        rospy.loginfo("=" * 50)

    def cleanup(self):
        rospy.loginfo("Shutting down SayHello node...")
        self.soundhandle.stopAll()

    def talkback(self, msg):
        global greet_flag

        faces = msg.faces
        face_count = len(faces)

        # Always log how many faces are detected
        rospy.loginfo(f"[Face Detection] Faces detected: {face_count}")

        if greet_flag == 0:
            if face_count > 0:
                rospy.loginfo(f"[Processing] Analysing {face_count} face(s)...")

                faces_data = []
                eyes_data  = []

                for i, face in enumerate(faces):
                    faces_data.append(face.face)
                    rospy.loginfo(f"  Face [{i}] position: x={face.face.x:.1f}, y={face.face.y:.1f}, "
                                  f"w={face.face.width:.1f}, h={face.face.height:.1f}")

                    if face.eyes:
                        rospy.loginfo(f"  Face [{i}] eyes detected: {face.eyes}")
                        eyes_data.append(face.eyes)
                    else:
                        rospy.logwarn(f"  Face [{i}] no eyes detected — skipping greeting")
                        eyes_data.append("null")

                # Check if any face has eyes confirmed
                valid_faces = [x for x in eyes_data if x != "null"]
                rospy.loginfo(f"[Check] Faces with eyes confirmed: {len(valid_faces)} / {face_count}")

                if valid_faces:
                    rospy.loginfo("[ACTION] Greeting guest — saying hello!")
                    self.soundhandle.say("Good morning. How can I help you?")
                    greet_flag = 1
                    rospy.loginfo("[State] greet_flag set to 1 — will not greet again until face leaves")
                else:
                    rospy.logwarn("[Skipped] Face(s) detected but no eyes confirmed — not greeting yet")
            else:
                rospy.loginfo("[Waiting] No faces in frame...")

        else:
            if face_count < 1:
                rospy.loginfo("[State] No faces detected — resetting greet_flag to 0")
                greet_flag = 0
            else:
                rospy.loginfo(f"[State] Already greeted — waiting for guest to leave (faces still: {face_count})")


if __name__ == "__main__":
    try:
        SayHello()
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("SayHello node terminated.")