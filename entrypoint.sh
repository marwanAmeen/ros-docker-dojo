#!/bin/bash
# ──────────────────────────────────────────────
#  ROS 1 Noetic container entrypoint
#  Auto-installs all dependencies on every start
# ──────────────────────────────────────────────
set -e

# ── 1. Install missing packages if not present ────────────────
echo "[entrypoint] Checking dependencies..."

# opencv_apps
if ! rospack find opencv_apps > /dev/null 2>&1; then
    echo "[entrypoint] Installing opencv_apps..."
    apt-get update -qq
    apt-get install -y -qq ros-noetic-opencv-apps
fi

# sound_play
if ! rospack find sound_play > /dev/null 2>&1; then
    echo "[entrypoint] Installing sound_play..."
    apt-get update -qq
    apt-get install -y -qq ros-noetic-sound-play
fi

# usb_cam
if ! rospack find usb_cam > /dev/null 2>&1; then
    echo "[entrypoint] Installing usb_cam..."
    apt-get update -qq
    apt-get install -y -qq ros-noetic-usb-cam
fi

# rqt_robot_steering
if ! rospack find rqt_robot_steering > /dev/null 2>&1; then
    echo "[entrypoint] Installing rqt_robot_steering..."
    apt-get update -qq
    apt-get install -y -qq ros-noetic-rqt-robot-steering
fi

# pulseaudio and alsa
if ! command -v paplay > /dev/null 2>&1; then
    echo "[entrypoint] Installing audio tools..."
    apt-get update -qq
    apt-get install -y -qq pulseaudio pulseaudio-utils alsa-utils libasound2-plugins
fi

# festival text to speech
if ! command -v festival > /dev/null 2>&1; then
    echo "[entrypoint] Installing festival TTS..."
    apt-get update -qq
    apt-get install -y -qq festival festvox-kallpc16k
fi

# cv_bridge and python opencv
if ! python3 -c "import cv2" > /dev/null 2>&1; then
    echo "[entrypoint] Installing cv_bridge and opencv..."
    apt-get update -qq
    apt-get install -y -qq ros-noetic-cv-bridge python3-opencv
fi

# haarcascades
if [ ! -f /usr/share/opencv4/haarcascades/haarcascade_frontalface_alt.xml ]; then
    echo "[entrypoint] Installing haarcascades..."
    apt-get update -qq
    apt-get install -y -qq opencv-data
fi

# ── 2. Haarcascades symlink ───────────────────────────────────
if [ ! -L /usr/share/opencv/haarcascades ]; then
    echo "[entrypoint] Creating haarcascades symlink..."
    mkdir -p /usr/share/opencv
    ln -sf /usr/share/opencv4/haarcascades /usr/share/opencv/haarcascades
fi

# ── 3. ALSA → PulseAudio routing ─────────────────────────────
if [ ! -f /etc/asound.conf ]; then
    echo "[entrypoint] Configuring ALSA to route through PulseAudio..."
    cat > /etc/asound.conf << 'ALSAEOF'
pcm.default pulseaudio
ctl.default pulseaudio

pcm.pulseaudio {
    type pulse
    server unix:/mnt/wslg/PulseServer
}

ctl.pulseaudio {
    type pulse
    server unix:/mnt/wslg/PulseServer
}
ALSAEOF
fi

# ── 4. Source ROS 1 base ──────────────────────────────────────
source /opt/ros/noetic/setup.bash

# ── 5. Source the catkin workspace overlay if it has been built
if [ -f /ros1_ws/devel/setup.bash ]; then
  source /ros1_ws/devel/setup.bash
fi

# ── 6. Friendly banner ────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   ROS 1 Noetic  —  $(hostname -s)         "
echo "║   ROS_MASTER_URI = ${ROS_MASTER_URI}      "
echo "║   DISPLAY        = ${DISPLAY}             "
echo "╚══════════════════════════════════════════╝"
echo ""

exec "$@"
