import rospy
import sys
from gazebo_msgs.srv import *
from geometry_msgs.msg import *
import tf.transformations as tft
import numpy as np
import math
import roslib
from std_msgs.msg import Empty as EmptyMsg
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
import time
from tools.mecanum_utils import *

max_vel_forward = 5.5 # m/s
max_vel_lateral = 1.5 # m/s

g_get_state = rospy.ServiceProxy("/gazebo/get_model_state", GetModelState)


def get_position():

    robot_state = g_get_state(model_name="mecanum")

    object_pose = Pose()
    object_pose.position.x = float(robot_state.pose.position.x)
    object_pose.position.y = float(robot_state.pose.position.y)
    object_pose.position.z = float(robot_state.pose.position.z)

    object_pose.orientation.x = float(robot_state.pose.orientation.x)
    object_pose.orientation.y = float(robot_state.pose.orientation.y)
    object_pose.orientation.z = float(robot_state.pose.orientation.z)
    object_pose.orientation.w = float(robot_state.pose.orientation.w)
    
    roll_x, pitch_y, yaw_z = qua2eular(object_pose.orientation.x, object_pose.orientation.y,
                                        object_pose.orientation.z, object_pose.orientation.w)

    return object_pose.position.x, object_pose.position.y, object_pose.position.z

def vel_threshold(x_vel, y_vel):

    if x_vel > 0:
        if abs(x_vel) > max_vel_forward:
            x_vel = max_vel_forward

    elif x_vel < 0:
        if abs(x_vel) > max_vel_forward:
            x_vel = -max_vel_forward

    if y_vel > 0:
        if abs(y_vel) > max_vel_lateral:
            y_vel = max_vel_lateral

    elif y_vel < 0:
        if abs(y_vel) > max_vel_lateral:
            y_vel = -max_vel_lateral

    return x_vel, y_vel

def apply_gravity():
    wrench = Wrench()
    duration = 1
    apply_wrench = rospy.ServiceProxy('/gazebo/apply_body_wrench', ApplyBodyWrench)
    body_name = 'mecanum::base_footprint'

    wrench.force = Vector3()

    wrench.force.x = 0
    wrench.force.y = 0
    wrench.force.z = int(-9.8 / 0.0001)

    success = apply_wrench(
        body_name,
        'world',
        Point(0, 0, 0),
        wrench,
        rospy.Time().now(),
        rospy.Duration(duration))


def move_mecanum(linear,angular_z):

    pub = rospy.Publisher("/mecanum_vel", Twist, queue_size=10)
    pub_wheel_vel_1 = rospy.Publisher("/mecanum/wheel_1_controller/command", Float64, queue_size=10)
    pub_wheel_vel_2 = rospy.Publisher("/mecanum/wheel_2_controller/command", Float64, queue_size=10)
    pub_wheel_vel_3 = rospy.Publisher("/mecanum/wheel_3_controller/command", Float64, queue_size=10)
    pub_wheel_vel_4 = rospy.Publisher("/mecanum/wheel_4_controller/command", Float64, queue_size=10)
    
    robot_state = g_get_state(model_name="mecanum")

    roll_x, pitch_y, yaw_z = qua2eular(robot_state.pose.orientation.x, 
                                        robot_state.pose.orientation.y, 
                                        robot_state.pose.orientation.z, 
                                        robot_state.pose.orientation.w)

    twist = Twist()

    x_vel, y_vel = vel_threshold(linear[0], linear[1])

    twist.linear.x = x_vel
    twist.linear.y = y_vel

    twist.angular.z = angular_z

    wheel_vel = mecanum_wheel_velocity(twist.linear.x, twist.linear.y, twist.angular.z)

    pub.publish(twist)
    pub_wheel_vel_1.publish(wheel_vel[0,:])
    pub_wheel_vel_2.publish(wheel_vel[1,:])
    pub_wheel_vel_3.publish(wheel_vel[2,:])
    pub_wheel_vel_4.publish(wheel_vel[3,:])

    return [x_vel, y_vel], angular_z



