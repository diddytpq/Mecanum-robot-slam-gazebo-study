import rospy

from geometry_msgs.msg import TransformStamped
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import tf
from tf.transformations import euler_from_quaternion, quaternion_from_euler

import numpy as np

def lidar_scan(msgScan):
    """
    Convert LaserScan msg to array
    """
    distances = np.array([])
    angles = np.array([])
    information = np.array([])

    for i in range(len(msgScan.ranges)):
        # angle calculation
        ang = i * msgScan.angle_increment

        # distance calculation
        if ( msgScan.ranges[i] > msgScan.range_max ):
            dist = msgScan.range_max
        elif ( msgScan.ranges[i] < msgScan.range_min ):
            dist = msgScan.range_min
        else:
            dist = msgScan.ranges[i]

        # smaller the distance, bigger the information (measurement is more confident)
        inf = ((msgScan.range_max - dist) / msgScan.range_max) ** 2 

        distances = np.append(distances, dist)
        angles = np.append(angles, ang)
        information = np.append(information, inf)

    # distances in [m], angles in [radians], information [0-1]
    return ( distances, angles, information )


def lidar_scan_xy(distances, angles, x_odom, y_odom, theta_odom):
	"""
	Lidar measurements in X-Y plane
	"""
	distances_x = np.array([])
	distances_y = np.array([])

	for (dist, ang) in zip(distances, angles):
		distances_x = np.append(distances_x, x_odom + dist * np.cos(ang + theta_odom))
		distances_y = np.append(distances_y, y_odom + dist * np.sin(ang + theta_odom))

	return (distances_x, distances_y)


def transform_orientation(orientation_q):
    """
    Transform theta to [radians] from [quaternion orientation]
    """
    orientation_list = [ orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
    (roll, pitch, yaw) = euler_from_quaternion(orientation_list)
    if yaw < 0:
        yaw = 2 * np.pi + yaw  # 0->360 degrees >> 0->2pi
    return yaw


def get_odom_orientation(msgOdom):
    """"
    Get theta from Odometry msg in [radians]
    """
    orientation_q = msgOdom.pose.pose.orientation
    theta = transform_orientation(orientation_q)
    return theta
    

def get_odom_position(msgOdom):
    """
    Get (x,y) coordinates from Odometry msg in [m]
    """
    x = msgOdom.pose.pose.position.x
    y = msgOdom.pose.pose.position.y
    return (x, y)


def get_tf_map_odom():

    trans_tf_pub = tf.TransformBroadcaster()

    ror_x, ror_y, ror_z, ror_w = quaternion_from_euler(np.deg2rad(0),np.deg2rad(0),np.deg2rad(0))

    # t = tf.Transformer(True, rospy.Duration(0.001))
    m = TransformStamped()
    m.header.frame_id = "map"
    # m.parent_id = "map"
    m.child_frame_id = "odom"
    m.transform.translation.x = 0
    m.transform.translation.y = 0
    m.transform.translation.z = 0
    m.transform.rotation.x = ror_x
    m.transform.rotation.y = ror_y
    m.transform.rotation.z = ror_z
    m.transform.rotation.w = ror_w


    trans_tf_pub.sendTransform([m.transform.translation.x, m.transform.translation.y, m.transform.translation.z], 
                                [m.transform.rotation.x, m.transform.rotation.y, m.transform.rotation.z, m.transform.rotation.w],  
                                rospy.Time.now(),
                                m.header.frame_id, 
                                m.child_frame_id)
    # t.setTransform(m)


def bresenham(gridMap, x1, y1, x2, y2):
	"""
	Bresenham's line drawing algorithm - working for all 4 quadrants!
	"""
	
	# Output pixels
	X_bres = []
	Y_bres = []

	x = x1
	y = y1
	
	delta_x = np.abs(x2 - x1)
	delta_y = np.abs(y2 - y1)
	
	s_x = np.sign(x2 - x1)
	s_y = np.sign(y2 - y1)

	if delta_y > delta_x:

		delta_x, delta_y = delta_y, delta_x
		interchange = True

	else:

		interchange = False

	A = 2 * delta_y
	B = 2 * (delta_y - delta_x)
	E = 2 * delta_y - delta_x

	# mark output pixels
	X_bres.append(x)
	Y_bres.append(y)

	# point (x2,y2) must not be included
	for i in range(1, delta_x):

		if E < 0:

			if interchange:

				y += s_y
			
			else:

				x += s_x

			E = E + A

		else:

			y += s_y
			x += s_x
			E = E + B

		# mark output pixels
		X_bres.append(x)
		Y_bres.append(y)

	return zip(X_bres, Y_bres)