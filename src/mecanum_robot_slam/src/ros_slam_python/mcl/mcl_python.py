import rospy
import numpy as np
from geometry_msgs.msg import PoseStamped, PoseArray, Point, Quaternion, Pose
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry, OccupancyGrid, MapMetaData
import message_filters
from particle import Particle
from scipy import misc
from copy import deepcopy
from tf.transformations import euler_from_quaternion, quaternion_from_euler
import cv2

import time
import sys
from pathlib import Path

FILE = Path(__file__).absolute()
sys.path.append(FILE.parents[0].as_posix())  # add code to path

path = str(FILE.parents[0])
sys.path.insert(0, path)


class Localizator:
    def __init__(self, init_x = False, init_y = False, init_yaw = False):     

        rospy.init_node('particle_filter', anonymous=True)
        self.rate = rospy.Rate(25) # 25hz

        self.frist_map_flag = 1

        self.pose_array_pub = rospy.Publisher("particlecloud", PoseArray, queue_size = 10)

        self.odom_sub = rospy.Subscriber("odom", Odometry, self.odom_callback)
        self.laser_sub = rospy.Subscriber("scan", LaserScan, self.laser_callback)
        self.ogrid_sub = rospy.Subscriber("map", OccupancyGrid, self.ogrid_callback)
   

        self.particles = []

        self.init_pos = (init_x, init_y, init_yaw)

        if self.init_pos[0] :
            self.num_of_particles = 300
        else:
            self.num_of_particles = 10000

        self.scan_msg = None
        self.odom_msg = None
        self.last_odom = None
        self.meter_to_pixel = 19.2 #pixel/meter

    def odom_callback(self, odom):
        if self.mutex == 0:        
            self.odom_msg = odom

        if self.last_odom is None:
            self.last_odom = odom


    def laser_callback(self, scan):
        if self.mutex == 0: 
            self.scan_msg = scan

    def ogrid_callback(self, ogrid):
        if self.frist_map_flag:
            self.ogrid_map = ogrid
            self.ogrid_width = ogrid.info.width
            self.ogrid_height = ogrid.info.height

            self.ogrid_origin_x = ogrid.info.origin.position.x
            self.ogrid_origin_y = ogrid.info.origin.position.y

            self.ogrid_map_np = np.array((ogrid.data)).reshape(self.ogrid_height,self.ogrid_width)

        self.frist_map_flag = 0

    def meter_pos_to_ogrid_pos(self, x, y):

        grid_x = int((abs(self.ogrid_origin_x) + x) * self.meter_to_pixel)
        grid_y = int((abs(self.ogrid_origin_y) + y) * self.meter_to_pixel)

        return grid_x, grid_y    
    
    def sigmoid(self, x):
        """Numerically-stable sigmoid function."""
        if x >= 0:
            z = np.exp(-x)
            return 1 / (1 + z)
        else:
            # if x is less than zero then z will be small, denom can't be
            # zero because it's 1+z.
            z = np.exp(x)
            return z / (1 + z)

    def move_particles(self):
        remove_indices = []
        if self.odom_msg is not None:
            # if self.last_odom is not None:
            q = self.odom_msg.pose.pose.orientation
            quaternion = [q.x, q.y, q.z, q.w]
            roll,pitch,yaw = euler_from_quaternion(quaternion)

            q_last = self.last_odom.pose.pose.orientation
            quaternion_last = [q_last.x, q_last.y, q_last.z, q_last.w]
            roll,pitch,yaw_last = euler_from_quaternion(quaternion_last)

            rot_1 = np.arctan2(self.odom_msg.pose.pose.position.y-self.last_odom.pose.pose.position.y, self.odom_msg.pose.pose.position.x - self.last_odom.pose.pose.position.x) - yaw_last
            trans = np.sqrt((self.odom_msg.pose.pose.position.x - self.last_odom.pose.pose.position.x) ** 2 + (self.odom_msg.pose.pose.position.y - self.last_odom.pose.pose.position.y) ** 2)
            rot_2 = yaw - yaw_last - rot_1

            for i in range(self.num_of_particles):
                new_x_pos = self.particles[i].x_pos + trans * np.cos(self.particles[i].yaw + rot_1)
                new_y_pos = self.particles[i].y_pos + trans * np.sin(self.particles[i].yaw + rot_1)
                new_yaw = self.particles[i].yaw + rot_1 + rot_2

                self.particles[i].set_x_pos(new_x_pos)
                self.particles[i].set_y_pos(new_y_pos)
                self.particles[i].set_yaw(new_yaw)

                grid_x, grid_y = self.meter_pos_to_ogrid_pos(new_x_pos, new_y_pos)

                if abs(new_x_pos) > abs(self.ogrid_origin_x) or \
                    abs(new_y_pos) > abs(self.ogrid_origin_y) or \
                    np.all(self.ogrid_map_np[grid_y][grid_x] > 99) :
                    remove_indices.append(i)

            self.last_odom = self.odom_msg
        cnt = 0
        for i in remove_indices:
            self.particles.pop(i - cnt)
            cnt += 1
            self.num_of_particles -= 1  
        print(self.num_of_particles)
            
    def sample_particles(self):

        time.sleep(1)

        if self.init_pos[0] == False:
            for i in range(self.num_of_particles):
                if self.frist_map_flag == 0 :
                    particle_x = (np.random.uniform(-abs(self.ogrid_origin_x), abs(self.ogrid_origin_x)))
                    particle_y = (np.random.uniform(-abs(self.ogrid_origin_y), abs(self.ogrid_origin_y)))
                    particle_yaw = (np.random.uniform(-np.pi, np.pi))

                    particle = Particle(particle_x, particle_y, particle_yaw)
                    self.particles.append(particle)     
                
        else:
            for i in range(self.num_of_particles):
                if self.frist_map_flag == 0 :
                    particle_x = (np.random.uniform((self.init_pos[0]) - 0.5, (self.init_pos[0] + 0.5)))
                    particle_y = (np.random.uniform((self.init_pos[1]) - 0.5, (self.init_pos[1] + 0.5)))
                    particle_yaw = self.init_pos[2]

                    particle = Particle(particle_x, particle_y, particle_yaw)
                    self.particles.append(particle)     
                

    def compute_weights(self):
        error_list = []
        new_particles = []

        if self.scan_msg is not None:
            for particle in self.particles:
                error = self.get_error_particle_observation(self.scan_msg, particle)

                error_list.append(error ** 2)

            self.weight_list = [np.exp(-error) for error in error_list]
            
            new_particles = self.particle_resample(self.weight_list, new_particles)

            sig_weight = [self.sigmoid(error) for error in error_list]
            N_eff_weight = sum([1 / (weight ** 2) for weight in sig_weight])
            N_eff = N_eff_weight

            if N_eff > 50:
                self.particles = new_particles


    def get_error_particle_observation(self, scan_msg, particle):

        sample_real_range_list, sample_real_angle_list = self.subsample_laser_scan(scan_msg)

        predict_range_list = self.sim_scan_based_particle(particle, sample_real_angle_list,scan_msg.range_min, scan_msg.range_max)

        diff = [actual_range - predict_range for actual_range, predict_range in zip(sample_real_range_list, predict_range_list)]

        norm_error = np.linalg.norm(diff)

        return norm_error

    def subsample_laser_scan(self, scan_msg):

        sample_real_range_list = []

        N = len(scan_msg.ranges)

        subsample_num = 36

        range_list = scan_msg.ranges
        angle_list = [scan_msg.angle_min + i * scan_msg.angle_increment for i in range(N)]

        step = int(N / subsample_num)

        sample_range_list = range_list[::step]
        sample_angle_list = angle_list[::step]

        for r in sample_range_list:

            if scan_msg.range_min < r < scan_msg.range_max :
                sample_real_range_list.append(r)
            elif r <= scan_msg.range_min:
                sample_real_range_list.append(scan_msg.range_min)
            else:
                sample_real_range_list.append(scan_msg.range_max)
                
        return sample_real_range_list, sample_angle_list

    def sim_scan_based_particle(self, particle, angle_list, range_min, range_max):

        sim_range_list = []

        for angle in angle_list:
            
            pred_angle = particle.yaw + angle
            r = range_min

            while r <= range_max:
                point_x = particle.x_pos + r * np.cos(pred_angle)
                point_y = particle.y_pos + r * np.sin(pred_angle)

                if abs(point_x) > abs(self.ogrid_origin_x) or abs(point_y) > abs(self.ogrid_origin_y):
                    break

                grid_x, grid_y = self.meter_pos_to_ogrid_pos(point_x, point_y)

                if self.ogrid_map_np[grid_y, grid_x] != 0:
                    break

                r += self.ogrid_map.info.resolution

            sim_range_list.append(r)
        
        return sim_range_list

    def particle_resample(self, weight_list, new_particles):
        
        beta = 0

        sample_u = np.random.uniform(0, 1)
        index = int(sample_u * (len(weight_list) - 1))

        weight_max = np.max(weight_list)

        for particle in self.particles:
            beta += np.random.uniform(0, 1) * 2 * weight_max

            while beta > self.weight_list[index]:
                beta -= self.weight_list[index]
                index = (index + 1) % len(weight_list)

            particle = self.particles[index]

            new_particles.append(Particle(particle.x_pos, particle.y_pos, particle.yaw))

        return new_particles


    def send_to_rviz(self, particles):
        pose_arr = PoseArray()
        pose_arr.header.frame_id = 'map'

        for particle in particles:
            particle_pos = PoseStamped()
            particle_pos.header.stamp = rospy.Time.now()
            particle_pos.header.frame_id = 'map'

            q = quaternion_from_euler(0,0,particle.yaw)

            particle_pos.pose = Pose(Point(particle.x_pos, particle.y_pos, 0),\
                                     Quaternion(q[0], q[1], q[2], q[3]))
            pose_arr.header = particle_pos.header
            pose_arr.poses.append(particle_pos.pose)

        self.pose_array_pub.publish(pose_arr)
        print("---------------------------------")

    def main(self):
        self.sample_particles()
        self.send_to_rviz(self.particles)

        while not rospy.is_shutdown():
            self.move_particles()
            self.compute_weights()
            self.send_to_rviz(self.particles)

if __name__ == '__main__':
    try:
        loc = Localizator(-3,1,0)
        # loc = Localizator()

        loc.main()
    except rospy.ROSInterruptException:
        pass