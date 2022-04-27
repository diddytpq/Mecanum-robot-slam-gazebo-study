#!/home/drcl-yang/anaconda3/envs/py37/bin/python3

import rospy

from geometry_msgs.msg import TransformStamped
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import tf
from tf.transformations import euler_from_quaternion, quaternion_from_euler

import numpy as np

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

rospy.init_node('trans_tf', anonymous = False)


if __name__ == "__main__":

    try :
        while not rospy.is_shutdown():
            get_tf_map_odom()
    except rospy.ROSInterruptException:
        pass