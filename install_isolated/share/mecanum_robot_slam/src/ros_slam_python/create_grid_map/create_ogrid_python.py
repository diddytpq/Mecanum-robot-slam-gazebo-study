#!/home/drcl-yang/anaconda3/envs/py37/bin/python3

import rospy
from nav_msgs.msg import OccupancyGrid, MapMetaData

import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter

import sys

SCRIPTS_PATH = '/home/workspace/Mecanum-robot-slam-gazebo/src/mecanum_robot_slam/scr'
MAPS_PATH = '/home/workspace/Mecanum-robot-slam-gazebo/src/mecanum_robot_slam/maps'
sys.path.insert(0, SCRIPTS_PATH)

from grid_map import *
from utils import *

P_prior = 0.5	# Prior occupancy probability
P_occ = 0.8	# Probability that cell is occupied with total confidence
P_free = 0.3	# Probability that cell is free with total confidence 

RESOLUTION = 0.05 # Grid resolution in [m]

MAP_NAME  = 'test' # map name without extension

MAP_SIZE = 10

if __name__ == '__main__':

    try:

        ogrid_pub = rospy.Publisher('python_map', OccupancyGrid, queue_size=1)
        

        # Init map parameters
        if MAP_NAME[:5] == 'stage':

            map_x_lim = [-3, 3]
            map_y_lim = [-3, 3]

        elif MAP_NAME[:5] == 'world':

            map_x_lim = [-4, 4]
            map_y_lim = [-4, 4]

        else:

            map_x_lim = [-MAP_SIZE, MAP_SIZE]
            map_y_lim = [-MAP_SIZE, MAP_SIZE]

        # Init ROS node
        rospy.init_node('gmapping_node', anonymous = False)
        rate = rospy.Rate(100)

        # Create grid map 
        gridMap = GridMap(X_lim = map_x_lim, 
                Y_lim = map_y_lim, 
                resolution = RESOLUTION, 
                p = P_prior)

        # Init time
        t_start = perf_counter()
        sim_time = 0
        step = 0

        # Main loop
        while not rospy.is_shutdown():

            # Lidar measurements
            msgScan = rospy.wait_for_message('/scan', LaserScan)
            distances, angles, information = lidar_scan(msgScan)  # distances in [m], angles in [radians]

            # Odometry measurements
            msgOdom = rospy.wait_for_message('/odom', Odometry)
            x_odom, y_odom = get_odom_position(msgOdom)   # x,y in [m]
            theta_odom = get_odom_orientation(msgOdom)    # theta in [radians]

            # Lidar measurements in X-Y plane
            distances_x, distances_y = lidar_scan_xy(distances, angles, x_odom, y_odom, theta_odom)

            # x1 and y1 for Bresenham's algorithm
            x1, y1 = gridMap.discretize(x_odom, y_odom)

            # for BGR image of the grid map
            X2 = []
            Y2 = []

            for (dist_x, dist_y, dist) in zip(distances_x, distances_y, distances):

                # x2 and y2 for Bresenham's algorithm
                x2, y2 = gridMap.discretize(dist_x, dist_y)

                # draw a discrete line of free pixels, [robot position -> laser hit spot)
                for (x_bres, y_bres) in bresenham(gridMap, x1, y1, x2, y2):

                    gridMap.update(x = x_bres, y = y_bres, p = P_free)

                # mark laser hit spot as ocuppied (if exists)
                if dist < msgScan.range_max:
                    
                    gridMap.update(x = x2, y = y2, p = P_occ)


            rviz_map = gridMap.numpy_to_occupancy_grid()
            ogrid_pub.publish(rviz_map)
            get_tf_map_odom()

            # Calculate step time in [s]
            t_step = perf_counter()
            step_time = t_step - t_start
            sim_time += step_time
            t_start = t_step
            step += 1 

            print('Step %d ==> %d [ms]' % (step, step_time * 1000))

            rate.sleep()

    except rospy.ROSInterruptException:
        cv2.destroyAllWindows()

        print('\r\nSIMULATION TERMINATED!')
        print('\nSimulation time: %.2f [s]' % sim_time)
        print('Average step time: %d [ms]' % (sim_time * 1000 / step))
        print('Frames per second: %.1f' % (step / sim_time))



        pass
