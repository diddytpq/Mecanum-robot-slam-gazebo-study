# Install script for directory: /home/yang/workspace/Mecanum-robot-slam-gazebo/src/mecanum_robot_gazebo

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
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/build/mecanum_robot_gazebo/catkin_generated/installspace/mecanum_robot_gazebo.pc")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/mecanum_robot_gazebo/cmake" TYPE FILE FILES
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/build/mecanum_robot_gazebo/catkin_generated/installspace/mecanum_robot_gazeboConfig.cmake"
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/build/mecanum_robot_gazebo/catkin_generated/installspace/mecanum_robot_gazeboConfig-version.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/mecanum_robot_gazebo" TYPE FILE FILES "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/mecanum_robot_gazebo/package.xml")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/mecanum_robot_gazebo" TYPE DIRECTORY FILES
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/mecanum_robot_gazebo/launch"
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/mecanum_robot_gazebo/models"
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/mecanum_robot_gazebo/worlds"
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/mecanum_robot_gazebo/src"
    "/home/yang/workspace/Mecanum-robot-slam-gazebo/src/mecanum_robot_gazebo/config"
    )
endif()

