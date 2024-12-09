import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ArrayElement:
    def __init__(self, position, phase_shift=0, frequency=1000, pattern_type='isotropic', frequencies=None):
        self.position = np.array(position)
        self.phase_shift = phase_shift
        self.frequency = frequency
        self.frequencies = frequencies if frequencies is not None else []
        self.pattern_type = pattern_type
        
    def calculate_field(self, point, time=0):
        distance = np.linalg.norm(point - self.position)
        k = 2 * np.pi * self.frequency / 343.0  # wavenumber
        # Calculate angle relative to element
        dx = point[0] - self.position[0]
        angle = np.arctan2(point[1] - self.position[1], dx)
        
        if self.pattern_type == 'isotropic':
            pattern = 1.0
        else:  # sinc pattern
            u = k * dx * np.sin(angle)
            pattern = np.sinc(u / np.pi)
        return pattern * np.exp(1j * (k * distance + self.phase_shift)) / max(distance, 0.1)