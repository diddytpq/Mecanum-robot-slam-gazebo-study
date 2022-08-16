#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/turtlebot_example/turtlebot3_teleop"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/yang/workspace/Mecanum-robot-slam-gazebo/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/yang/workspace/Mecanum-robot-slam-gazebo/install/lib/python3/dist-packages:/home/yang/workspace/Mecanum-robot-slam-gazebo/build/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/yang/workspace/Mecanum-robot-slam-gazebo/build" \
    "/usr/bin/python3" \
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/turtlebot_example/turtlebot3_teleop/setup.py" \
     \
    build --build-base "/home/yang/workspace/Mecanum-robot-slam-gazebo/build/turtlebot_example/turtlebot3_teleop" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/home/yang/workspace/Mecanum-robot-slam-gazebo/install" --install-scripts="/home/yang/workspace/Mecanum-robot-slam-gazebo/install/bin"
