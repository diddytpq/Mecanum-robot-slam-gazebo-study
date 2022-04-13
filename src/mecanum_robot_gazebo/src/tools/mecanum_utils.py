import numpy as np
import math

def Ttorpm(T):
    
    r = 0.065
    v0 = T * 0.01


    return v0 * 9.549297


def cal(force, T):
    a = np.sqrt((force[0])**2 + (force[2])**2) / 0.057
    v0 = a *0.01

    rpm = Ttorpm(T[1])

    return v0 , rpm

    

def rotation_matrix(angle):

    return np.array([[np.cos(angle),-np.sin(angle),0],
             [np.sin(angle),np.cos(angle),0],
             [0,0,1]])

def get_wrench(force, torque, matrix):

    F = matrix@(np.array(force).reshape([3,1]))
    T = matrix@(np.array(torque).reshape([3,1]))
    
    F = F.reshape([1,3]).tolist()
    T = T.reshape([1,3]).tolist()


    return F[0], T[0]

def qua2eular(x,y,z,w):

    q_x = x
    q_y = y
    q_z = z
    q_w = w

    t0 = +2.0 * (q_w * q_x + q_y * q_z)
    t1 = +1.0 - 2.0 * (q_x * q_x + q_y * q_y)
    roll_x = math.atan2(t0, t1)

    t2 = +2.0 * (q_w * q_y - q_z * q_x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)

    t3 = +2.0 * (q_w * q_z + q_x * q_y)
    t4 = +1.0 - 2.0 * (q_y * q_y + q_z * q_z)
    yaw_z = math.atan2(t3, t4)

    return roll_x, pitch_y, yaw_z # in radians


def mecanum_wheel_velocity(vx, vy, wz):
    r = 0.0762 # radius of wheel
    l = 0.23 #length between {b} and wheel
    w = 0.25225 #depth between {b} abd wheel
    alpha = l + w
    
    q_dot = np.array([wz, vx, vy])
    J_pseudo = np.array([[-alpha, 1, -1],[alpha, 1, 1],[alpha, 1, -1],[alpha, 1,1]])

    u = 1/r * J_pseudo @ np.reshape(q_dot,(3,1))#q_dot.T

    return u