execute_process(COMMAND "/home/drcl/workspace/Mecanum-robot-slam-gazebo/build/turtlebot_example/turtlebot3_teleop/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/drcl/workspace/Mecanum-robot-slam-gazebo/build/turtlebot_example/turtlebot3_teleop/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
