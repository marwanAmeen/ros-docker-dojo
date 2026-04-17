# 🥋 ros-docker-dojo

> A hands-on ROS1 Noetic learning environment running entirely in Docker on Windows WSL2 — no robot hardware required.

[![ROS Noetic](https://img.shields.io/badge/ROS-Noetic-blue?logo=ros)](http://wiki.ros.org/noetic)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docs.docker.com/compose/)
[![WSL2](https://img.shields.io/badge/Windows-WSL2-0078D4?logo=windows)](https://learn.microsoft.com/en-us/windows/wsl/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What is this?

**ros-docker-dojo** is a complete ROS1 Noetic development environment that runs inside Docker on Windows WSL2. It was built to practice ROS concepts from scratch without needing a physical robot — including nodes, topics, publishers, subscribers, launch files, custom messages, face detection, and audio output.

The highlight is a fully simulated camera pipeline that replaces real hardware:

```
video file
    ↓
camera_simulator  →  /usb_cam/image_raw
        ↓
face_detection    →  /face_detection/faces
        ↓
say_hello node
        ↓
soundplay_node    →  🔊 "Good morning. How can I help you?"
```

---

## 🗂️ Repository Structure

```
ros-docker-dojo/
├── docker-compose.yml          # Three services: roscore, ros-base, ros-desktop
├── entrypoint.sh               # Auto-installs all dependencies on startup
├── .env                        # DISPLAY and ROS environment variables
└── ws/                         # Catkin workspace (mounted into containers)
    └── src/
        ├── my_robot_tutorials/ # Practice nodes — publishers, subscribers, custom msgs
        │   ├── CMakeLists.txt
        │   ├── package.xml
        │   ├── scripts/
        │   │   ├── my_first_node.py
        │   │   ├── path_correction_node.py
        │   │   └── motion_planning_node.py
        │   ├── launch/
        │   │   └── my_first_launch.launch
        │   └── msg/
        │       └── PathCorrection.msg
        ├── camera_simulator/   # Simulated camera node
        │   ├── CMakeLists.txt
        │   ├── package.xml
        │   ├── scripts/
        │   │   └── camera_simulator.py
        │   ├── launch/
        │   │   └── camera_sim.launch
        │   └── videos/
        │       └── test.mp4    ← put your test video here
        └── rc-home-edu-learn-ros/  # Juno2 robot course packages
            └── rchomeedu_vision/
                ├── scripts/
                │   └── say_hello_ans.py
                └── launch/
                    └── say_hello_ans.launch
```

---

## 🐳 Services

| Service | Image | Purpose |
|---|---|---|
| `roscore` | `ros:noetic-ros-core` | ROS master — must always run first |
| `ros-base` | `ros:noetic-ros-base` | catkin_make, writing nodes, CLI tools |
| `ros-desktop` | `osrf/ros:noetic-desktop-full` | turtlesim, rqt, rviz, running nodes |

---

## ⚙️ Prerequisites

- Windows 10/11 with WSL2
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2 backend
- [VcXsrv](https://sourceforge.net/projects/vcxsrv/) for GUI (X11 display)

---

## 🚀 Quick Start

### 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ros-docker-dojo.git
cd ros-docker-dojo
```

### 2 — Set DISPLAY in WSL2
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```

### 3 — Start VcXsrv on Windows
Launch **XLaunch** with:
- Display number: `0`
- Start no client
- ☑ Disable access control

### 4 — Start containers
```bash
docker compose up -d
```

The `entrypoint.sh` will automatically install all dependencies on first start including `opencv_apps`, `sound_play`, `festival` TTS, haarcascades, and PulseAudio routing.

### 5 — Open a shell
```bash
docker exec -it ros1_desktop bash
source /opt/ros/noetic/setup.bash
source /ros1_ws/devel/setup.bash
```

---

## 📚 Exercises Covered

### Part 1 — ROS Basics
- Creating a catkin workspace and packages
- Writing Python nodes with class structure
- Publishers and subscribers
- Custom message types (.msg files)
- Launch files

### Part 2 — Topics and Nodes
- TurtleSim — launching, controlling, debugging
- rostopic / rosnode CLI tools
- Anonymous nodes
- Publishing geometry_msgs/Twist to move robots
- rqt_graph for visualising the node graph

### Part 3 — Face Detection Pipeline
- Camera simulator node (no hardware needed)
- opencv_apps face detection with Haar cascades
- say_hello node with sound_play audio output
- Full pipeline from video → face detection → speech

---

## 🔊 Audio Setup (WSLg)

Audio is routed through WSLg PulseAudio. The `entrypoint.sh` handles this automatically by writing `/etc/asound.conf` to redirect ALSA through PulseAudio:

```
ALSA → PulseAudio → WSLg PulseServer → Windows audio
```

The `docker-compose.yml` mounts `/mnt/wslg` and sets `PULSE_SERVER=unix:/mnt/wslg/PulseServer`.

---

## 🎬 Launch the Face Detection Pipeline

**Terminal 1 — Camera simulator + face detection**
```bash
docker exec -it ros1_desktop bash
source /opt/ros/noetic/setup.bash
source /ros1_ws/devel/setup.bash
roslaunch camera_simulator camera_sim.launch
```

**Terminal 2 — Say hello node**
```bash
docker exec -it ros1_desktop bash
source /opt/ros/noetic/setup.bash
source /ros1_ws/devel/setup.bash
roslaunch rchomeedu_vision say_hello_ans.launch
```

**Verify all nodes are running**
```bash
rosnode list
```

Expected:
```
/camera_simulator
/face_detection
/say_hello
/soundplay_node
/rosout
```

---

## 🛠️ Common Commands

```bash
# Build workspace
cd /ros1_ws && catkin_make
source devel/setup.bash

# List all nodes
rosnode list

# List all topics
rostopic list

# Watch messages on a topic
rostopic echo /topic_name

# Measure publish rate
rostopic hz /topic_name

# Move turtlesim
rostopic pub -1 /turtle1/cmd_vel geometry_msgs/Twist \
  '{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}'
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `rosnode: command not found` | `source /opt/ros/noetic/setup.bash` |
| `CRLF` line ending error | `tr -d '\r' < file.py > /tmp/fix.py && cp /tmp/fix.py file.py` |
| No GUI window | Make sure VcXsrv is running with Disable access control checked |
| No audio | Check `echo $PULSE_SERVER` shows `unix:/mnt/wslg/PulseServer` |
| Haarcascade error | `apt-get install -y opencv-data && ln -sf /usr/share/opencv4/haarcascades /usr/share/opencv/haarcascades` |
| `use_sim_time` warning | `rosparam set /use_sim_time false` then restart nodes |
| Package not found after restart | Entrypoint auto-reinstalls — wait for it to finish |

---

## 📖 References

- [ROS Noetic Documentation](http://wiki.ros.org/noetic)
- [rospy API](http://wiki.ros.org/rospy)
- [roscpp API](http://wiki.ros.org/roscpp)
- [opencv_apps](http://wiki.ros.org/opencv_apps)
- [sound_play](http://wiki.ros.org/sound_play)
- [Juno2 Robot — Jupiter Robot Technology](http://jupiterobot.com)

---

## 📝 License

MIT License — feel free to use, modify and share.
