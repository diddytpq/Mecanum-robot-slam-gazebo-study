#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 16:50:27 2018
@author: EmaPajic
"""

import rospy
import numpy as np
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class Navigator:
    def __init__(self):
        self.scan_msg = None
        rospy.init_node('navigation', anonymous=True)
        self.rate = rospy.Rate(25) # 25hz
        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size = 5)
        self.safety_vel = rospy.Publisher('cmd_vel_mux/input/safety_controller', Twist, queue_size = 1)
        rospy.Subscriber('scan', LaserScan, self.callback) 
        
    def callback(self, msg):
        self.scan_msg = msg
        
    def safety_check(self):
        if self.scan_msg is not None:
             for i in range(len(self.scan_msg.ranges)):
		    r = self.scan_msg.ranges[i]
                    if r > self.scan_msg.range_min and r < self.scan_msg.range_max:
                        if r < max(self.scan_msg.range_min + 0.5, 0.5):
			    tmp = (self.scan_msg.angle_min + self.scan_msg.angle_increment * i)
			    if tmp < 0.5 and tmp > -0.5:
				self.move_angular_cmd(safety = True, min_angle = 90, max_angle = 270)
			    elif tmp < 0:
                            	self.move_angular_cmd(safety = True, min_angle = 20, max_angle = 90)
			    else:
				self.move_angular_cmd(safety = True, min_angle = -90, max_angle = -20)
                            break
                        
    def move_linear_cmd(self, min_speed = 0, max_speed = 1):
        move_cmd = Twist()
        move_cmd.linear.x = np.random.uniform(min_speed,max_speed)
        self.cmd_vel.publish(move_cmd)
        self.rate.sleep()
        
    def move_angular_cmd(self, safety, min_angle = -180, max_angle = 180, probability = 1):
        if np.random.uniform(0,1) < probability: 
            turn_cmd = Twist()
            turn_cmd.angular.z = np.radians(np.random.uniform(min_angle,max_angle))
            if safety == True:
                self.safety_vel.publish(turn_cmd)
            else:
                self.cmd_vel.publish(turn_cmd)
            self.rate.sleep()
        
    def navigation(self):
        while not rospy.is_shutdown():
            self.safety_check()
            self.move_linear_cmd(0,1)
            self.move_angular_cmd(safety = False, probability = 0.4)
        
if __name__ == '__main__':
    try:
        nav = Navigator()
        nav.navigation()
    except rospy.ROSInterruptException:
        pass
