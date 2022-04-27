from tk import Tk, Canvas, PhotoImage, mainloop
from math import sin
from scipy import misc
import numpy as np
from particle import Particle
#window = Tk()


class mapDrawer:

    def __init__(self, window):
        self.window = window        
        self.img_location = "/home/user/catkin_ws/src/navigation/scripts/slam_map.png"
        self.img = PhotoImage(file=self.img_location)
        self.old_img = misc.imread(self.img_location)
        self.WIDTH_OF_IMAGE = self.img.width()
        self.HEIGHT_OF_IMAGE = self.img.height()
        self.number_of_particles = np.zeros(shape=(self.HEIGHT_OF_IMAGE, self.WIDTH_OF_IMAGE))
        self.canvas = Canvas(window, width=self.WIDTH_OF_IMAGE*2, height=self.HEIGHT_OF_IMAGE*2, bg="#000000")
        self.canvas.pack()
        self.canvas.create_image((self.WIDTH_OF_IMAGE/2, self.HEIGHT_OF_IMAGE/2), image=self.img, state="normal")
        self.old_red_pixels = []
        self.meter_to_pixel = 30.8
    def clamp(self, x):
        return max(0, min(x, 255))
    
    def convert_to_six_digit_code(self, color):
        r, g, b = color
        return "#{0:02x}{1:02x}{2:02x}".format(self.clamp(r), self.clamp(g), self.clamp(b))
    
    def restore_old_image(self):
        for position in self.old_red_pixels:
            width, height = position
            self.img.put(self.convert_to_six_digit_code(self.old_img[height][width]), (width, height))
            self.old_red_pixels = []
    
    def draw_circle(self, i, j, diameter):
        min_width = max(0, i - diameter)
        max_width = min(self.WIDTH_OF_IMAGE - 1, i + diameter)
        min_height = max(0, j - diameter)
        max_height = min(self.HEIGHT_OF_IMAGE - 1, j + diameter)
        for curr_width in range(int(min_width), int(max_width + 1)):
            for curr_height in range(int(min_height), int(max_height + 1)):
                if self.img.get(curr_width, curr_height) == "#ff0000":
                    continue
                if np.sqrt((i - curr_width)**2 + (j - curr_height)**2) <= diameter:
                    self.img.put("#ff0000", (curr_width, curr_height))
                    self.old_red_pixels.append((curr_width, curr_height))

    def update(self, num_of_particles_per_pixel):
    
        total_num_of_particles = 0
        for value in num_of_particles_per_pixel:
            total_num_of_particles += num_of_particles_per_pixel.get(value, 0)
            self.restore_old_image()
            for value in num_of_particles_per_pixel:
                percentage = float(num_of_particles_per_pixel.get(value, 0)) / total_num_of_particles
                if(percentage > 0):
                    self.draw_circle(value % self.WIDTH_OF_IMAGE, value / self.WIDTH_OF_IMAGE, int(int(percentage / 0.15) + 1))
        self.window.update()

    def update_particles(self, particles):
        number_of_particles_per_pixel = {}        
        for particle in particles:
            height_in_pixels = int(particle.get_height() * self.meter_to_pixel)
            width_in_pixels  = int(particle.get_width()  * self.meter_to_pixel)
            index = height_in_pixels * self.WIDTH_OF_IMAGE + width_in_pixels
            number_of_particles_per_pixel[index] = number_of_particles_per_pixel.get(index, 0) + particle.get_cnt()
        self.update(number_of_particles_per_pixel)



"""
map = mapDrawer(window)
lista = []
for i in range(0,10):
    lista.append(Particle(50,100,1))
for j in range(0,3):
    lista.append(Particle(20,20,1))
lista.append(Particle(50,50,1))
map.update_particles(lista)

while(1):
    map.update_particles(lista)
    for particle in lista:
    particle.set_width((particle.get_width() + int(np.random.uniform(-1,1) * 2)) % 100)
    particle.set_height((particle.get_height() + int(np.random.uniform(-1,1) * 2)) % 100)

window.mainloop()
"""
