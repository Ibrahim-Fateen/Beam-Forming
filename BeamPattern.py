
import numpy as np
from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from Array import Array


class PolarPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(15, 15))
        # self.figure.tight_layout()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111, projection='polar')
        self.ax.set_thetamin(-180)
        self.ax.set_thetamax(0)
        self.ax.set_theta_zero_location('E')
        self.ax.set_theta_direction(-1)
        self.figure.tight_layout()
        self.ax.set_position([0.0, -0.3, 1, 1.6])

        layout.addWidget(self.canvas)
    def update_plot(self,array:Array):
        if len(array.components) == 0:
            self.ax.clear()
            self.ax.set_thetamin(-180)
            self.ax.set_thetamax(0)
            self.ax.set_theta_zero_location('E')
            self.ax.set_theta_direction(-1)
            self.canvas.draw()
            return
        theta = np.linspace(0, -np.pi, 500)
        af = array.calculate_beam_pattern(theta)
        # standardize the plot to be above 0
        af = af - np.min(af)
        # Find the minimum wavelength (highest frequency) component
        min_wavelength = array.c / min([comp.frequency for comp in array.components])
        # Scale the array factor based on wavelength
        scaling_factor = min_wavelength / 0.1  # 0.1 is a reference wavelength
        af = af * scaling_factor
        self.ax.clear()
        self.ax.set_thetamin(-180)
        self.ax.set_thetamax(0)
        self.ax.set_theta_zero_location('E')
        self.ax.set_theta_direction(-1)
        self.figure.tight_layout()
        self.ax.plot(theta, af)

        # Calculate tick values based on af range
        max_af = np.max(af)
        tick_count = 5
        tick_values = np.linspace(0, max_af, tick_count)
        self.ax.set_rticks(tick_values)
        self.ax.set_rlim(0, max_af)
        
        self.ax.grid(True)
        self.ax.set_position([0.0, -0.3, 1, 1.6])
        self.canvas.draw()
