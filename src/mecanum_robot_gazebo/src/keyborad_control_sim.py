#!/home/yoseph/anaconda3/envs/py37/bin/python3

import rospy
import numpy as np
from std_msgs.msg import Float64
from gazebo_msgs.srv import *
from geometry_msgs.msg import *
import sys, select, os
import roslib

if os.name == 'nt':
  import msvcrt
else:
  import tty, termios

from tools.mecanum_key_utils import *

roslib.load_manifest('mecanum_robot_gazebo')


accel = 0.3

def getKey():
    if os.name == 'nt':
      if sys.version_info[0] >= 3:
        return msvcrt.getch().decode()
      else:
        return msvcrt.getch()

    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

if __name__ == '__main__':
    try:
        rospy.init_node('mecanum_key')
        if os.name != 'nt':
            settings = termios.tcgetattr(sys.stdin)
        linear = [0, 0]
        angular_z = 0
        while(1):
            # apply_gravity()
            
            key = getKey()

            if key == 'w' :

                linear[0] += accel 
                linear, angular_z = move_mecanum(linear, angular_z)

            elif key == 'x' :
                linear[0] -= accel
                linear, angular_z = move_mecanum(linear, angular_z)

            elif key == 'a' :
                linear[1] += accel
                linear, angular_z = move_mecanum(linear, angular_z)

            elif key == 'd' :
                linear[1] -= accel
                linear, angular_z = move_mecanum(linear, angular_z)

            elif key == 'q' :
                angular_z += 0.3
                linear, angular_z = move_mecanum(linear, angular_z)

            elif key == 'e' :
                angular_z -= 0.3
                linear, angular_z = move_mecanum(linear, angular_z)

            elif key == 's' :
                linear = [0, 0]
                angular_z = 0
                linear, angular_z = move_mecanum(linear, angular_z)
                
            if (key == '\x03'):
                linear = [0, 0]
                angular_z = 0
                linear, angular_z = move_mecanum(linear, angular_z)
                break

    except rospy.ROSInt:
        pass
