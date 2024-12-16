
import numpy as np
from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from Array import Array

# class PolarPlotWidget(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setup_ui()
        
#     def setup_ui(self):
#         layout = QVBoxLayout()
#         self.figure = Figure(figsize=(12, 8))
#         self.canvas = FigureCanvasQTAgg(self.figure)
#         self.ax_polar = self.figure.add_subplot(111, projection='polar')
#         self.figure.tight_layout()
#         layout.addWidget(self.canvas)
#         self.setLayout(layout)
        
#     def update_plot(self, array):
#         self.ax_polar.clear()
        
#         # Polar beam pattern plot
#         theta = np.linspace(0, np.pi, 30)
#         pattern = np.zeros_like(theta, dtype=complex)
        
#         center = array.center
#         r = 2.0
#         for angle, i in zip(theta, range(len(theta))):
#             point = r * np.array([np.cos(angle), np.sin(angle)]) + center
#             for element in array.elements:
#                 pattern[i] += element.calculate_field(point)
        
#         epsilon = 1e-10
#         pattern_db = 20 * np.log10(np.abs(pattern) + epsilon)
#         pattern_db = np.maximum(pattern_db, -40)
        
#         self.ax_polar.plot(theta, pattern_db + 40)
#         self.ax_polar.set_title('Polar Beam Pattern')
#         self.ax_polar.set_theta_zero_location('E')
#         self.ax_polar.set_theta_direction(1)
#         self.ax_polar.set_rlabel_position(90)
#         self.ax_polar.grid(True)
        
#         angles = np.arange(0, 360, 30)
#         self.ax_polar.set_thetagrids(angles, labels=[f'{angle}°' for angle in angles])
        
#         self.figure.tight_layout()
#         self.canvas.draw()

class PolarPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(6, 6))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111, projection='polar')
        layout.addWidget(self.canvas)

    def update_plot(self,array:Array):

        theta = np.linspace(-np.pi, np.pi, 1000)
        af = array.calculate_array_factor(theta)

        self.ax.clear()
        af_norm = af - np.max(af)
        af_norm = np.clip(af_norm, -40, 0)
        self.ax.plot(theta, af_norm + 40)
        self.ax.set_rticks([0, 10, 20, 30, 40])
        self.ax.set_rlim(0, 40)
        self.ax.grid(True)
        self.canvas.draw()