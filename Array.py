import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from ArrayElement import ArrayElement
class Array:
    def __init__(self, center=(0,0), num_elements=8, radius=1.0, curvature=0.0, rotation=0.0):
        self.center = np.array(center)
        self.num_elements = num_elements
        self.radius = radius
        self.curvature = curvature
        self.rotation = rotation
        self.elements = []
        self.steering_angle = 0
        self.create_array()
        
    def rotate_point(self, point, angle_deg):
        angle_rad = np.radians(angle_deg)
        rotation_matrix = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
        ])
        return np.dot(rotation_matrix, point - self.center) + self.center
        
    def create_array(self):
        self.elements.clear()
        if self.curvature == 0.0:  # linear array
            spacing = self.radius / max(1, self.num_elements - 1)
            for i in range(self.num_elements):
                base_pos = self.center + np.array([-self.radius/2 + i*spacing, 0])
                rotated_pos = self.rotate_point(base_pos, self.rotation)
                self.elements.append(ArrayElement(rotated_pos))
        else:  # curved array
            for i in range(self.num_elements):
                angle = -(i / (self.num_elements - 1)) * np.pi * self.curvature
                base_pos = self.center + self.radius * np.array([np.cos(angle), np.sin(angle)])
                rotated_pos = self.rotate_point(base_pos, self.rotation)
                self.elements.append(ArrayElement(rotated_pos))
    
    def set_steering_angle(self, angle):
        self.steering_angle = angle
        k = 2 * np.pi * self.elements[0].frequency / 343.0
        d = self.radius / (self.num_elements - 1)
        for i, element in enumerate(self.elements):
            element.phase_shift = -k * d * i * np.sin(np.radians(angle))