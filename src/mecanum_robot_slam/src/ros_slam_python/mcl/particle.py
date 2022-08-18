#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 17:17:11 2018

@author: EmaPajic
"""

class Particle:
    def __init__(self, x_pos = 0, y_pos = 0, yaw = 0):
        self.x_pos = x_pos
        self.y_pos = y_pos 
        self.yaw = yaw
        self.cnt = 1
    
    def set_x_pos(self, x_pos):
        self.x_pos= x_pos
    
    def set_y_pos(self, y_pos):
        self.y_pos  = y_pos 

    def set_yaw(self, yaw):
        self.yaw = yaw
        
    def set_cnt(self, cnt):
        self.cnt = cnt
