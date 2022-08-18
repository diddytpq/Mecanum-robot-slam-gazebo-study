
import rospy
import numpy as np
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import message_filters
from particle import Particle
from scipy import misc
from copy import deepcopy
from tf.transformations import euler_from_quaternion
import cv2

class Localizator:
    def __init__(self):        
        self.map_width = 1610
        self.map_height = 2550
        self.map_path = "slam_map.png"
        self.map = cv2.imread(self.map_path)
        self.map = cv2.resize(self.map,(self.map_width,self.map_height))
        self.particles = []
        self.mutex = 0
        self.sum_of_weights = 0.0
        self.particle_weights = []
        self.num_of_particles = 1000
        self.scan_msg = None
        self.odom_msg = None
        self.last_odom = None
        self.meter_to_pixel = 30.8
        # self.window = Tk()
        # self.map_drawer = mapDrawer(self.window)
        rospy.init_node('particle_filter', anonymous=True)
        self.rate = rospy.Rate(25) # 25hz
        self.odom_sub = rospy.Subscriber("odom", Odometry, self.odom_callback)
        self.laser_sub = rospy.Subscriber("scan", LaserScan, self.laser_callback)

    def move_particles(self):
        remove_indices = []
        if self.odom_msg is not None:
            if self.last_odom is not None:
                for i in range(self.num_of_particles):
                    new_width = self.particles[i].get_width() - \
                    self.odom_msg.pose.pose.position.y + self.last_odom.pose.pose.position.y
                    self.particles[i].set_width(new_width)
                    new_height = self.particles[i].get_height() - \
                    self.odom_msg.pose.pose.position.x + self.last_odom.pose.pose.position.x
                    self.particles[i].set_height(new_height)
                    new_width *= self.meter_to_pixel
                    new_height *= self.meter_to_pixel
            if new_height < 0 or new_height > (self.map_height) or new_width < 0 or new_width > (self.map_width) or np.all(self.map[int(new_height)][int(new_width)] > [100,100,100]):
                remove_indices.append(i)

            self.last_odom = self.odom_msg
        cnt = 0
        for i in remove_indices:
            self.particles.pop(i - cnt)
            cnt += 1
            self.num_of_particles -= 1  
                
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
                        if r > self.scan_msg.range_min and r < self.scan_msg.range_max:
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
                particle_width = int(np.random.uniform(0, self.map_width))
                particle_height = int(np.random.uniform(0, self.map_height))
                if np.any(self.map[particle_height][particle_width] != 2550):
                    break
            particle = Particle(particle_width / self.meter_to_pixel, particle_height / self.meter_to_pixel)
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
    
    def odom_callback(self, odom):
        if self.mutex == 0:        
            self.odom_msg = odom

    def laser_callback(self, scan):
        if self.mutex == 0: 
            self.scan_msg = scan

    def particle_filter(self):
        self.sample_particles()
        while not rospy.is_shutdown():
            self.compute_weights()
            self.resample_particles()
            self.map_drawer.update_particles(self.particles)
            self.window.update()
            for i in range(0,10):
                self.move_particles()
                self.map_drawer.update_particles(self.particles)
                self.window.update()
                self.rate.sleep()
    
if __name__ == '__main__':
    try:
        loc = Localizator()
        loc.particle_filter()
    except rospy.ROSInterruptException:
        pass
