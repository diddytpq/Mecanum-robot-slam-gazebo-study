import rospy
import numpy as np
from geometry_msgs.msg import PoseStamped, PoseArray, Point, Quaternion, Pose
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry, OccupancyGrid, MapMetaData
from particle import Particle
from copy import deepcopy
from tf.transformations import euler_from_quaternion, quaternion_from_euler

from scipy.stats import norm

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

        self.scan_msg = None
        self.odom_msg = None
        self.last_odom = None
        self.meter_to_pixel = 20 #pixel/meter

        self.frist_map_flag = 1
        self.std_dev = 1
        self.mutex = 0

        self.pose_array_pub = rospy.Publisher("particlecloud", PoseArray, queue_size = 10)

        self.odom_sub = rospy.Subscriber("odom", Odometry, self.odom_callback)
        self.laser_sub = rospy.Subscriber("scan", LaserScan, self.laser_callback)
        self.ogrid_sub = rospy.Subscriber("map", OccupancyGrid, self.ogrid_callback)
   
        self.particles = []

        self.init_pos = (init_x, init_y, init_yaw)

        if self.init_pos[0] :
            self.num_of_particles = 10
        else:
            self.num_of_particles = 1000



    def odom_callback(self, odom):
        if self.mutex == 0:        
            self.odom_msg = odom

        if self.last_odom is None:
            self.last_odom = odom

    def laser_callback(self, scan):
        if self.mutex == 0: 
            self.scan_msg = scan

    def ogrid_callback(self, ogrid):
        if self.mutex == 0: 
            # if self.frist_map_flag:
            self.ogrid_map = ogrid
            self.ogrid_width = ogrid.info.width
            self.ogrid_height = ogrid.info.height

            self.ogrid_origin_x = ogrid.info.origin.position.x
            self.ogrid_origin_y = ogrid.info.origin.position.y

            self.ogrid_map_np = np.array((ogrid.data)).reshape(self.ogrid_height,self.ogrid_width)

            self.ogrid_map_occ_pos_list = []

            for i in range(self.ogrid_width):
                for j in range(self.ogrid_height):
                    if self.ogrid_map_np[j][i] == 100:
                        self.ogrid_map_occ_pos_list.append([i,j])
            print(len(self.ogrid_map_occ_pos_list))
        # self.frist_map_flag = 0

    def meter_pos_to_ogrid_pos(self, x, y):

        grid_x = int((abs(self.ogrid_origin_x - x)) * self.meter_to_pixel)
        # grid_y = self.ogrid_height - int((abs(self.ogrid_origin_y - y)) * self.meter_to_pixel)
        grid_y = int((abs(self.ogrid_origin_y - y)) * self.meter_to_pixel)

        return grid_x, grid_y
    

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
        print("num_of_particles = ",self.num_of_particles)
            
    def sample_particles(self):

        time.sleep(1)

        if self.init_pos[0] == False:
            for i in range(self.num_of_particles):
                while True:
                    particle_x = (np.random.uniform(-abs(self.ogrid_origin_x), abs(self.ogrid_origin_x)))
                    particle_y = (np.random.uniform(-abs(self.ogrid_origin_y), abs(self.ogrid_origin_y)))
                    particle_yaw = (np.random.uniform(-np.pi, np.pi))

                    # particle_x = (np.random.uniform(-abs(self.ogrid_origin_x), abs(self.ogrid_origin_x)))
                    # particle_y = (np.random.uniform(-abs(self.ogrid_origin_y), abs(self.ogrid_origin_y)))
                    # particle_yaw = (np.random.uniform(-np.pi, np.pi))

                    # particle_x = 0
                    # particle_y = 3
                    # particle_yaw = 0

                    x_pixel, y_pixel = self.meter_pos_to_ogrid_pos(particle_x ,particle_y)

                    if (self.ogrid_map_np[y_pixel][x_pixel]) == 0:
                        particle = Particle(particle_x, particle_y, particle_yaw)
                        self.particles.append(particle)
                        break
                
        else:
            for i in range(self.num_of_particles):

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

                self.weight_list.append(weight ** 1)

        if self.weight_list:
            self.sum_of_weights = sum(self.weight_list)

            if self.sum_of_weights < 1e-15:
                self.weight_list = [weight/self.num_of_particles for weight in range(len(self.weight_list))]
                self.sum_of_weights = 1

            else:
                self.weight_list = [weight/self.sum_of_weights for weight in range(len(self.weight_list))]
                self.sum_of_weights = 1

            print("sum_of_weights = ",self.sum_of_weights)
            # self.weight_list = [np.exp(np.log(1000 * np.exp(-error))) for error in error_list]
            
            # new_particles = self.particle_resample(weight_list, new_particles)

            # self.particles = new_particles

    def particle_likelihood(self, particle):
        cnt = 0
        self.mutex = 1

        weight = 1

        if self.scan_msg is not None:
            if self.odom_msg is not None:			
                q = self.odom_msg.pose.pose.orientation
                quaternion = [q.x, q.y, q.z, q.w]
                roll,pitch,yaw = euler_from_quaternion(quaternion)
                for i in range(len(self.scan_msg.ranges)):
                    if i % 20  == 0:
                        r = self.scan_msg.ranges[i]
                        if r > self.scan_msg.range_min and r < self.scan_msg.range_max:
                            cnt += 1
                            pixel_length = int(r * self.meter_to_pixel)
                            pixel_angle = yaw + self.scan_msg.angle_min + self.scan_msg.angle_increment * i
                            ogrid_x, ogrid_y = self.meter_pos_to_ogrid_pos(particle.x_pos, particle.y_pos)
                            object_x = int(ogrid_x + int(pixel_length * np.cos(pixel_angle)))
                            object_y = int(ogrid_y + int(pixel_length * np.sin(pixel_angle)))

                            dist = pixel_length

                            for occ_pos in self.ogrid_map_occ_pos_list:
                                current_dist = np.sqrt((object_x - occ_pos[0]) ** 2 + (object_y - occ_pos[1]) ** 2)

                                if current_dist < dist:
                                    dist = current_dist

                        prob = norm(scale=self.std_dev).pdf(dist * self.ogrid_map.info.resolution)

                        if prob >= 1:
                            prob = 1

                        weight *= np.float32(prob)

        self.mutex = 0	
        if cnt == 0:
            return 0
        # print(dist)
        print("weight",weight)			
        return weight

    def resample_particles(self):
        # if self.sum_of_weights == 0:
        #     return
        # new_particles = []
        # cum_sums = np.cumsum(self.weight_list).tolist()
        # print(cum_sums)
        # initial_weight = 1.0 / self.num_of_particles
        
        # num = 0

        # self.weight_list = np.array(self.weight_list) / self.sum_of_weights
        
        # for i in range(self.num_of_particles):
        #     u = np.random.uniform(1e-6, 1, 1)[0]
        #     m = 0
        #     while cum_sums[m] < u:
        #         m += 1

        #     new_particle = Particle(self.particles[m].x_pos,self.particles[m].y_pos, self.particles[m].yaw)
        #     num += 1
            
        #     new_particles.append(new_particle)


        # self.particles = deepcopy(new_particles)
        # self.num_of_particles = num
        
        ###########################################################################

        if self.sum_of_weights == 0:
            return
        new_particles = []
        dictionary = {}

        num = 0

        for i in range(self.num_of_particles):
            temp = np.random.uniform(0, self.sum_of_weights)
            sum_until_temp = 0.0
            for j in range(self.num_of_particles):
                sum_until_temp += self.weight_list[j]
                if temp < sum_until_temp:
                    x, y, yaw = self.particles[j].x_pos,self.particles[j].y_pos, self.particles[j].yaw
                    # new_particle = Particle(x, y, yaw)
                    # new_particle.set_cnt(1)
                    # new_particles.append(new_particle)

                    new_x = (np.random.uniform(x - 0.05, x + 0.05))
                    new_y = (np.random.uniform(y - 0.05, y + 0.05))
                    new_yaw = (np.random.uniform(yaw - (np.pi/20), yaw + (np.pi/20)))

                    new_particle = Particle(new_x,new_y,new_yaw)
                    new_particle.set_cnt(1)
                    new_particles.append(new_particle)
                    num += 1
                    break

        self.num_of_particles = num

        # if self.num_of_particles < 15 :
        #     for particle in self.particles:
        #         x, y, yaw = particle.x_pos, particle.y_pos, particle.yaw

        #         new_x = (np.random.uniform(x - 0.5, x + 0.5))
        #         new_y = (np.random.uniform(y - 0.5, y + 0.5))
        #         new_yaw = (np.random.uniform(yaw - (np.pi), yaw + (np.pi)))

        #         new_particle = Particle(new_x,new_y,new_yaw)
        #         new_particle.set_cnt(1)
        #         new_particles.append(new_particle)

        #         self.num_of_particles += 1

        self.particles = deepcopy(new_particles)

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
            # self.compute_weights()
            # self.resample_particles()
            self.send_to_rviz(self.particles)
            print("dt = ", time.time() - t0)

if __name__ == '__main__':
    try:
        # loc = Localizator(-3,1,0)
        loc = Localizator()

        loc.main()
    except rospy.ROSInterruptException:
        pass