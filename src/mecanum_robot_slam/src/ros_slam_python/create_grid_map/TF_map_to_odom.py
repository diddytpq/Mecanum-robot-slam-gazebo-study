#!/home/yoseph/anaconda3/envs/py37/bin/python3

import rospy

from geometry_msgs.msg import TransformStamped
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import tf2_ros
import tf2_msgs.msg
from tf.transformations import euler_from_quaternion, quaternion_from_euler

import numpy as np

def get_tf_map_odom():
    pub_tf = rospy.Publisher("/tf", tf2_msgs.msg.TFMessage, queue_size=1)

    t = TransformStamped()
    t.header.frame_id = "map"
    t.header.stamp = rospy.Time.now()
    t.child_frame_id = "odom"
    t.transform.translation.x = 0.0
    t.transform.translation.y = 0.0
    t.transform.translation.z = 0.0

    t.transform.rotation.x = 0.0
    t.transform.rotation.y = 0.0
    t.transform.rotation.z = 0.0
    t.transform.rotation.w = 1.0

    tfm = tf2_msgs.msg.TFMessage([t])
    pub_tf.publish(tfm)


rospy.init_node('trans_tf', anonymous = False)


if __name__ == "__main__":

    try :
        while not rospy.is_shutdown():
            rospy.sleep(0.1)
            get_tf_map_odom()
    except rospy.ROSInterruptException:
        pass
