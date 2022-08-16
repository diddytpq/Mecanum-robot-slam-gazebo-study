# Install script for directory: /home/yang/workspace/Mecanum-robot-slam-gazebo/src/trajectory_planner_pkg/far_planner_pkg/visibility_graph_msg

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/yang/workspace/Mecanum-robot-slam-gazebo/install")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/visibility_graph_msg/msg" TYPE FILE FILES
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/trajectory_planner_pkg/far_planner_pkg/visibility_graph_msg/msg/Node.msg"
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/trajectory_planner_pkg/far_planner_pkg/visibility_graph_msg/msg/Graph.msg"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/visibility_graph_msg/cmake" TYPE FILE FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/build/trajectory_planner_pkg/far_planner_pkg/visibility_graph_msg/catkin_generated/installspace/visibility_graph_msg-msg-paths.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE DIRECTORY FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/devel/include/visibility_graph_msg")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roseus/ros" TYPE DIRECTORY FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/devel/share/roseus/ros/visibility_graph_msg")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/common-lisp/ros" TYPE DIRECTORY FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/devel/share/common-lisp/ros/visibility_graph_msg")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/gennodejs/ros" TYPE DIRECTORY FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/devel/share/gennodejs/ros/visibility_graph_msg")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  execute_process(COMMAND "/usr/bin/python3" -m compileall "/home/yang/workspace/Mecanum-robot-slam-gazebo/devel/lib/python3/dist-packages/visibility_graph_msg")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python3/dist-packages" TYPE DIRECTORY FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/devel/lib/python3/dist-packages/visibility_graph_msg")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/build/trajectory_planner_pkg/far_planner_pkg/visibility_graph_msg/catkin_generated/installspace/visibility_graph_msg.pc")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/visibility_graph_msg/cmake" TYPE FILE FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/build/trajectory_planner_pkg/far_planner_pkg/visibility_graph_msg/catkin_generated/installspace/visibility_graph_msg-msg-extras.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/visibility_graph_msg/cmake" TYPE FILE FILES
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/build/trajectory_planner_pkg/far_planner_pkg/visibility_graph_msg/catkin_generated/installspace/visibility_graph_msgConfig.cmake"
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/build/trajectory_planner_pkg/far_planner_pkg/visibility_graph_msg/catkin_generated/installspace/visibility_graph_msgConfig-version.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/visibility_graph_msg" TYPE FILE FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/trajectory_planner_pkg/far_planner_pkg/visibility_graph_msg/package.xml")
endif()

