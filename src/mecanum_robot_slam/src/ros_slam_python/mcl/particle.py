#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 17:17:11 2018

@author: EmaPajic
"""

class Particle:
    def __init__(self, width = 0, height = 0):
        self.width = width
        self.height = height
        self.cnt = 1
        
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height

    def get_cnt(self):
        return self.cnt
    
    def set_width(self, width):
        self.width = width
    
    def set_height(self, height):
        self.height = height

    def set_cnt(self, cnt):
        self.cnt = cnt
