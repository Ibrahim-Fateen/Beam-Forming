import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from ArrayElement import ArrayElement

class Array:
    def __init__(self, center=(0,0), num_elements=8, geometry='linear', radius=1.0):
        self.center = np.array(center)
        self.num_elements = num_elements
        self.geometry = geometry
        self.radius = radius
        self.elements = []
        self.create_array()
        
    def create_array(self):
        self.elements.clear()
        if self.geometry == 'linear':
            spacing = self.radius / max(1, self.num_elements - 1)
            for i in range(self.num_elements):
                pos = self.center + np.array([-self.radius/2 + i*spacing, 0])
                self.elements.append(ArrayElement(pos))
        else:  # curved
            for i in range(self.num_elements):
                angle = -(i / (self.num_elements - 1) ) * np.pi
                pos = self.center + self.radius * np.array([np.cos(angle), np.sin(angle)])
                self.elements.append(ArrayElement(pos))

    def set_steering_angle(self, angle):
        k = 2 * np.pi * self.elements[0].frequency / 343.0
        d = self.radius / (self.num_elements - 1)
        for i, element in enumerate(self.elements):
            element.phase_shift = -k * d * i * np.sin(np.radians(angle))