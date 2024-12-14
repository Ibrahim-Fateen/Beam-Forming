
import numpy as np
from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure



class PolarPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax_polar = self.figure.add_subplot(111, projection='polar')
        self.figure.tight_layout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def update_plot(self, array):
        self.ax_polar.clear()
        
        # Polar beam pattern plot
        theta = np.linspace(0, np.pi, 30)
        pattern = np.zeros_like(theta, dtype=complex)
        
        center = array.center
        r = 2.0
        for angle, i in zip(theta, range(len(theta))):
            point = r * np.array([np.cos(angle), np.sin(angle)]) + center
            for element in array.elements:
                pattern[i] += element.calculate_field(point)
        
        epsilon = 1e-10
        pattern_db = 20 * np.log10(np.abs(pattern) + epsilon)
        pattern_db = np.maximum(pattern_db, -40)
        
        self.ax_polar.plot(theta, pattern_db + 40)
        self.ax_polar.set_title('Polar Beam Pattern')
        self.ax_polar.set_theta_zero_location('E')
        self.ax_polar.set_theta_direction(1)
        self.ax_polar.set_rlabel_position(90)
        self.ax_polar.grid(True)
        
        angles = np.arange(0, 360, 30)
        self.ax_polar.set_thetagrids(angles, labels=[f'{angle}°' for angle in angles])
        
        self.figure.tight_layout()
        self.canvas.draw()