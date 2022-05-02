import rospy
import numpy as np
from geometry_msgs.msg import PoseStamped, PoseArray, Point, Quaternion, Pose
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry, OccupancyGrid, MapMetaData
import message_filters
from particle import Particle
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
        self.mutex = 0

        self.pose_array_pub = rospy.Publisher("particlecloud", PoseArray, queue_size = 10)

        self.odom_sub = rospy.Subscriber("odom", Odometry, self.odom_callback)
        self.laser_sub = rospy.Subscriber("scan", LaserScan, self.laser_callback)
        self.ogrid_sub = rospy.Subscriber("map", OccupancyGrid, self.ogrid_callback)
   

        self.particles = []

        self.init_pos = (init_x, init_y, init_yaw)

        if self.init_pos[0] :
            self.num_of_particles = 30
        else:
            self.num_of_particles = 1000

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

        grid_x = int((abs(self.ogrid_origin_x - x)) * self.meter_to_pixel)
        grid_y = self.ogrid_height - int((abs(self.ogrid_origin_y - y)) * self.meter_to_pixel)

        return grid_x, grid_y - 1
    

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
                while True:
                    if self.frist_map_flag == 0 :
                        particle_x = (np.random.uniform(-abs(self.ogrid_origin_x), abs(self.ogrid_origin_x)))
                        particle_y = (np.random.uniform(-abs(self.ogrid_origin_y), abs(self.ogrid_origin_y)))
                        particle_yaw = (np.random.uniform(-np.pi, np.pi))

                        x_pixel, y_pixel = self.meter_pos_to_ogrid_pos(particle_x ,particle_y)

                        if np.all(self.ogrid_map_np[y_pixel][x_pixel]) == 0:
                            particle = Particle(particle_x, particle_y, particle_yaw)
                            self.particles.append(particle)
                            break

                
        else:
            for i in range(self.num_of_particles):
                if self.frist_map_flag == 0 :
                    particle_x = (np.random.uniform((self.init_pos[0]) - 0.5, (self.init_pos[0] + 0.5)))
                    particle_y = (np.random.uniform((self.init_pos[1]) - 0.5, (self.init_pos[1] + 0.5)))
                    particle_yaw = self.init_pos[2]

                    particle = Particle(particle_x, particle_y, particle_yaw)
                    self.particles.append(particle)     
                

    def compute_weights(self):
        self.weight_list = []
        self.sum_of_weights = 0

        if self.scan_msg is not None:
            for particle in self.particles:
                weight = self.particle_likelihood(particle)

                self.weight_list.append(weight ** 2)

        if self.weight_list:
            self.sum_of_weights = sum(self.weight_list)
            
            print(self.sum_of_weights)
            # self.weight_list = [np.exp(np.log(1000 * np.exp(-error))) for error in error_list]
            
            # new_particles = self.particle_resample(weight_list, new_particles)

            # self.particles = new_particles

    def particle_likelihood(self, particle):
        similarity = 0
        cnt = 0
        self.mutex = 1
    
        if self.scan_msg is not None:
            if self.odom_msg is not None:			
                q = self.odom_msg.pose.pose.orientation
                quaternion = [q.x, q.y, q.z, q.w]
                roll,pitch,yaw = euler_from_quaternion(quaternion)
                for i in range(len(self.scan_msg.ranges)):
                    if i % 10 == 0:
                        r = self.scan_msg.ranges[i]
                        if r > self.scan_msg.range_min and r < self.scan_msg.range_max:
                            cnt += 1
                            pixel_length = int(r * self.meter_to_pixel)
                            pixel_angle = yaw + self.scan_msg.angle_min + self.scan_msg.angle_increment * i
                            ogrid_x, ogrid_y = self.meter_pos_to_ogrid_pos(particle.x_pos, particle.y_pos)
                            wall_x = int(ogrid_x + int(pixel_length * np.cos(pixel_angle)))
                            wall_y = int(ogrid_y - int(pixel_length * np.sin(pixel_angle)))
                            for k in range(-3,3):
                                for j in range(-3,3): 
                                    wall_x1 = wall_x + k
                                    wall_y1 = wall_y + j
                                    if wall_x1 >= 0 and wall_x1 < self.ogrid_width and wall_y1 >= 0 and wall_y1 < self.ogrid_height:          
                                        if np.any(self.ogrid_map_np[int(wall_y1)][int(wall_x1)] > 99):
                                                similarity += 1
                                                break	
        self.mutex = 0	
        if cnt == 0:
            return 0			
        return 100 * particle.cnt * similarity/cnt

    def resample_particles(self):
        if self.sum_of_weights == 0:
            return
        new_particles = []
        dictionary = {}
        for i in range(self.num_of_particles + 50):
            temp = np.random.uniform(0, self.sum_of_weights)
            sum_until_temp = 0.0
            for j in range(self.num_of_particles):
                sum_until_temp += self.weight_list[j]
                if temp < sum_until_temp:
                    if self.particles[j] in dictionary:
                        dictionary[tuple((self.particles[j].x_pos,self.particles[j].y_pos))] += 1
                    else:
                        dictionary[tuple((self.particles[j].x_pos,self.particles[j].y_pos))] = 1
                    break
        num = 0
        for key in dictionary:
            a,b = key
            new_particle = Particle(a,b)
            new_particle.set_cnt(dictionary[key])
            new_particles.append(new_particle)
            num += 1
            
            self.particles = deepcopy(new_particles)
        self.num_of_particles = num



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
            t0 = time.time()
            self.move_particles()
            self.compute_weights()
            self.resample_particles()
            self.send_to_rviz(self.particles)
            print("dt = ", time.time() - t0)

if __name__ == '__main__':
    try:
        # loc = Localizator(-3,1,0)
        loc = Localizator()

        loc.main()
    except rospy.ROSInterruptException:
        pass