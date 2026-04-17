# ROS 1 Noetic — Docker Compose (Part 2 Practice)

## File layout

```
ros1/
├── docker-compose.yml   # three services: roscore, ros-base, ros-desktop
├── entrypoint.sh        # sources ROS + workspace on startup
└── ws/                  # your catkin workspace (create manually first)
    └── src/
        └── your_package/
```

---

## Services

| Service       | Image                          | Use case                                      |
|---------------|--------------------------------|-----------------------------------------------|
| `roscore`     | `ros:noetic-ros-core`          | ROS master — must always be running first      |
| `ros-base`    | `ros:noetic-ros-base`          | catkin_make, rospy/roscpp, publisher/subscriber |
| `ros-desktop` | `osrf/ros:noetic-desktop-full` | turtlesim, rostopic/rosnode CLI tools, rqt     |

> **Key ROS 1 difference vs ROS 2**: every session needs a `roscore` running.  
> In ROS 2 there is no master — DDS handles discovery automatically.

---

## 1 — Create the workspace first (host side)

```bash
mkdir -p ws/src
```

---

## 2 — Pull images (one-time, ~2–5 GB)

```bash
docker compose pull
```

---

## 3 — Start all services

```bash
# Start roscore + both shells detached
docker compose up -d

# Open a base shell (for catkin_make, writing code)
docker exec -it ros1_base bash -c "echo 'source /opt/ros/noetic/setup.bash' >> ~/.bashrc"
docker exec -it ros1_base bash

# Open a desktop shell (for turtlesim, rostopic, rosnode)
docker exec -it ros1_desktop bash -c "echo 'source /opt/ros/noetic/setup.bash' >> ~/.bashrc"
docker exec -it ros1_desktop bash
```

Or run a single service interactively:

```bash
docker compose up roscore -d          # master must be detached in background
docker compose run --rm ros-desktop   # interactive desktop shell
```

---

## 4 — Part 2 Practice Workflow

### Smoke test — check everything is connected

```bash
# In any shell
rosnode list          # should show /rosout
rostopic list         # should show /rosout and /rosout_agg
```

---

### Turtlesim (Testing Nodes)

Open two terminals into `ros1_desktop`:

```bash
# Terminal 1 — launch the turtle window
rosrun turtlesim turtlesim_node

# Terminal 2 — drive it with keyboard
rosrun turtlesim turtle_teleop_key
```

**Debug commands to try:**

```bash
rosnode list                          # see all running nodes
rosnode info /turtlesim               # topics published/subscribed, services
rosnode ping /turtlesim               # check node is alive
rostopic list                         # all active topics
rostopic echo /turtle1/cmd_vel        # watch velocity messages in real time
rostopic info /turtle1/cmd_vel        # publisher, subscribers, message type
```

---

### Topics — Python Publisher & Subscriber

Set up your catkin workspace in `ros-base`:

```bash
# Inside ros1_base
cd /ros1_ws
catkin_make                           # build (first time, creates devel/)
source devel/setup.bash

# Create a package with rospy + std_msgs
cd src
catkin_create_pkg my_robot_pkg rospy roscpp std_msgs
cd /ros1_ws && catkin_make
source devel/setup.bash
```

**Python publisher** (`src/my_robot_pkg/scripts/robot_news_radio_transmitter.py`):

```python
#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

rospy.init_node('robot_news_radio_transmitter')
pub = rospy.Publisher('/robot_news_radio', String, queue_size=10)
rate = rospy.Rate(2)  # 2 Hz

while not rospy.is_shutdown():
    msg = String()
    msg.data = "Hi, this is Dan from the Robot News Radio"
    pub.publish(msg)
    rate.sleep()

rospy.on_shutdown(lambda: rospy.loginfo("Node was stopped"))
```

```bash
chmod +x src/my_robot_pkg/scripts/robot_news_radio_transmitter.py
rosrun my_robot_pkg robot_news_radio_transmitter.py
```

**Python subscriber** (`src/my_robot_pkg/scripts/smartphone.py`):

```python
#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

def callback(msg):
    rospy.loginfo(f"I heard: {msg.data}")

rospy.init_node('smartphone')
rospy.Subscriber('/robot_news_radio', String, callback)
rospy.spin()
```

---

### Topics — C++ Publisher & Subscriber

**C++ publisher** (`src/my_robot_pkg/src/robot_news_radio_transmitter.cpp`):

```cpp
#include <ros/ros.h>
#include <std_msgs/String.h>

int main(int argc, char **argv) {
    ros::init(argc, argv, "robot_news_radio_transmitter");
    ros::NodeHandle nh;
    ros::Publisher pub = nh.advertise<std_msgs::String>("/robot_news_radio", 10);
    ros::Rate rate(3);  // 3 Hz

    while (ros::ok()) {
        std_msgs::String msg;
        msg.data = "Hi, this is William from the Robot News Radio";
        pub.publish(msg);
        rate.sleep();
    }
    return 0;
}
```

Add to **CMakeLists.txt**:

```cmake
add_executable(robot_news_radio_transmitter src/robot_news_radio_transmitter.cpp)
target_link_libraries(robot_news_radio_transmitter ${catkin_LIBRARIES})

add_executable(smartphone_node src/smartphone_node.cpp)
target_link_libraries(smartphone_node ${catkin_LIBRARIES})
```

```bash
cd /ros1_ws && catkin_make
source devel/setup.bash
rosrun my_robot_pkg robot_news_radio_transmitter
```

---

### Debugging Topics (instead of rqt_graph)

```bash
rostopic list                         # all active topics
rostopic info /robot_news_radio       # who publishes, who subscribes, msg type
rostopic echo /robot_news_radio       # watch live messages
rostopic pub -1 /robot_news_radio std_msgs/String "data: 'hello world'"   # publish once
rostopic pub -r 5 /robot_news_radio std_msgs/String "data: 'hello world'" # publish at 5 Hz
rostopic hz /robot_news_radio         # measure publish rate
rostopic bw /robot_news_radio         # measure bandwidth

rosnode list
rosnode info /robot_news_radio_transmitter
rosnode ping /smartphone
```

These CLI tools give you full visibility into the ROS graph without needing rqt_graph.

---

### Anonymous nodes (fixing same-name conflicts)

In Python:
```python
rospy.init_node('robot_news_radio_transmitter', anonymous=True)
```

In C++:
```cpp
ros::init(argc, argv, "robot_news_radio_transmitter", ros::init_options::AnonymousName);
```

---

## 5 — Stop everything

```bash
docker compose down
```

---

## Tips

- **roscore must always be running** before any `rosrun` or node launch.
- Both `ros-base` and `ros-desktop` connect to the same `roscore` via the `ros1_net` bridge network.
- The shared `./ws` volume means code you write in `ros-base` is instantly visible in `ros-desktop` and vice versa.
- `network_mode: host` is **not** used here — containers talk to each other via the named bridge and resolve `roscore` by hostname.
