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

import sys
from pathlib import Path

FILE = Path(__file__).absolute()
sys.path.append(FILE.parents[0].as_posix())  # add code to path

path = str(FILE.parents[0])
sys.path.insert(0, path)


class Localizator:
    def __init__(self):        
        self.map_width = 384
        self.map_height = 384
        self.map_path = path + "/map/house.pgm"
        self.map = cv2.imread(self.map_path)
        self.map = cv2.resize(self.map,(self.map_width,self.map_height))
        self.ogrid_map = 0
        self.particles = []
        self.mutex = 0
        self.sum_of_weights = 0.0
        self.particle_weights = []
        self.num_of_particles = 1000
        self.scan_msg = None
        self.odom_msg = None
        self.last_odom = None
        self.meter_to_pixel = 19.2 #pixel/meter
        # self.window = Tk()
        # self.map_drawer = mapDrawer(self.window)
        rospy.init_node('particle_filter', anonymous=True)
        self.rate = rospy.Rate(25) # 25hz

        self.frist_map_flag = 1

        self.pose_array_pub = rospy.Publisher("particlecloud", PoseArray, 10)

        self.odom_sub = rospy.Subscriber("odom", Odometry, self.odom_callback)
        self.laser_sub = rospy.Subscriber("scan", LaserScan, self.laser_callback)
        self.ogrid_sub = rospy.Subscriber("map", OccupancyGrid, self.ogrid_callback)

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

            self.ogrid_origin_x = self.ogrid_map.info.origin.position.x
            self.ogrid_origin_y = self.ogrid_map.info.origin.position.y

            self.ogrid_map_np = np.array((ogrid.data)).reshape(self.ogrid_height,self.ogrid_width)

        self.frist_map_flag = 0

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
                new_width = self.particles[i].get_width() + trans * np.cos(self.particles[i].get_yaw() + rot_1)
                new_height = self.particles[i].get_height() + trans * np.sin(self.particles[i].get_yaw() + rot_1)
                new_yaw = self.particles[i].get_yaw() + rot_1 + rot_2

                self.particles[i].set_width(new_width)
                self.particles[i].set_height(new_height)
                self.particles[i].set_yaw(new_yaw)

                if abs(new_width) > abs(self.ogrid_origin_x) or \
                    abs(new_height) > abs(self.ogrid_origin_y) or \
                    np.all(self.ogrid_map_np[int((10 + new_height) * self.meter_to_pixel)][int((-10 + new_width) * self.meter_to_pixel)] > 99):
                    # np.all(self.ogrid_map_np[int(new_height * self.meter_to_pixel)][int(new_width * self.meter_to_pixel)] > 99):     
                    remove_indices.append(i)

            self.last_odom = self.odom_msg
        cnt = 0
        for i in remove_indices:
            self.particles.pop(i - cnt)
            cnt += 1
            self.num_of_particles -= 1  
        print(self.num_of_particles)
                
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
                    if i % 5 == 0:
                        r = self.scan_msg.ranges[i]
                        if self.scan_msg.range_min < r < self.scan_msg.range_max:
                            cnt += 1
                            pixel_length = int(r * self.meter_to_pixel)
                            pixel_angle = yaw + self.scan_msg.angle_min + self.scan_msg.angle_increment * i
                            wall_x = int(particle.get_height() * self.meter_to_pixel - int(pixel_length * np.cos(pixel_angle)))
                            wall_y = int(particle.get_width() * self.meter_to_pixel - int(pixel_length * np.sin(pixel_angle)))
                            for k in range(-5,6):
                                for j in range(-5,6): 
                                    wall_x1 = wall_x + k
                                    wall_y1 = wall_y + j
                                    if wall_x1 >= 0 and wall_x1 < self.map_height and wall_y1 >= 0 and wall_y1 < self.map_width:          
                                        if np.all(self.map[int(wall_x1)][int(wall_y1)] > [100,100,100]):
                                                similarity += 1
                                            
                                                break	
        self.mutex = 0	
        if cnt == 0:
            return 0			
        return 100 * particle.get_cnt() * similarity/cnt
            
    def sample_particles(self):
        for i in range(self.num_of_particles):
            while True:
                if self.frist_map_flag == 0 :
                    particle_width = int(np.random.uniform(-abs(self.ogrid_origin_x), abs(self.ogrid_origin_x)))
                    particle_height = int(np.random.uniform(-abs(self.ogrid_origin_y), abs(self.ogrid_origin_y)))

                    particle_yaw = (np.random.uniform(-np.pi, np.pi))

                    if np.any(self.map[particle_height][particle_width] != 2550):
                        break
            particle = Particle(particle_width, particle_height, particle_yaw)
            self.particles.append(particle)     
            
    def resample_particles(self):
        if self.sum_of_weights == 0:
            return
        new_particles = []
        dictionary = {}
        for i in range(self.num_of_particles + 50):
            temp = np.random.uniform(0, self.sum_of_weights)
            sum_until_temp = 0.0
            for j in range(self.num_of_particles):
                sum_until_temp += self.particle_weights[j]
                if temp < sum_until_temp:
                    if self.particles[j] in dictionary:
                        dictionary[tuple((self.particles[j].get_width(),self.particles[j].get_height()))] += 1
                    else:
                        dictionary[tuple((self.particles[j].get_width(),self.particles[j].get_height()))] = 1
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

    def compute_weights(self):
        self.sum_of_weights = 0.0
        self.particle_weights = []
        for particle in self.particles:
            particle_weight = self.particle_likelihood(particle)**(3)
            self.particle_weights.append(particle_weight)
            self.sum_of_weights += particle_weight
    
    def print_particles(self, particles):
        # number_of_particles_per_pixel = {}  
        pose_arr = PoseArray()
        pose_arr.header.frame_id = 'map'

        for particle in particles:
            particle_pos = PoseStamped()
            particle_pos.header.stamp = rospy.Time.now()
            particle_pos.header.frame_id = 'map'
            
            # height_in_pixels = int(particle.get_height() * self.meter_to_pixel)
            # width_in_pixels  = int(particle.get_width()  * self.meter_to_pixel)
            # index = height_in_pixels * self.map_width + width_in_pixels
            # number_of_particles_per_pixel[index] = number_of_particles_per_pixel.get(index, 0) + particle.get_cnt()

            q = quaternion_from_euler(0,0,particle.get_yaw())

            particle_pos.pose = Pose(Point(particle.get_width(), particle.get_height(), 0),\
                                     Quaternion(q[0], q[1], q[2], q[3]))
            pose_arr.header = particle_pos.header
            pose_arr.poses.append(particle_pos.pose)



            # print(height_in_pixels,width_in_pixels)
            # print(particle.get_height(),particle.get_width(), np.rad2deg(particle.get_yaw()))
        self.pose_array_pub.publish(pose_arr)
        print("---------------------------------")

    def particle_filter(self):
        self.sample_particles()
        while not rospy.is_shutdown():
            # self.compute_weights()
            # self.resample_particles()
            # self.map_drawer.update_particles(self.particles)
            # self.print_particles(self.particles)
            self.move_particles()
            self.print_particles(self.particles)

        #     # self.window.update()
        #     for i in range(0,10):
        # #         # self.map_drawer.update_particles(self.particles)
        # #         # self.window.update()
        #         self.rate.sleep()

            # if self.ogrid_map:
            #     print(np.array((self.ogrid_map)).reshape(self.ogrid_height,self.ogrid_width).shape)

if __name__ == '__main__':
    try:
        loc = Localizator()
        loc.particle_filter()
    except rospy.ROSInterruptException:
        pass