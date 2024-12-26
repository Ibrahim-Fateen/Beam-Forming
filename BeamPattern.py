
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

        theta = np.linspace(0, -np.pi, 300)
        af = array.calculate_beam_pattern(theta)

        self.ax.clear()
        self.ax.set_thetamin(-180)
        self.ax.set_thetamax(0)
        self.ax.set_theta_zero_location('E')
        self.ax.set_theta_direction(-1)
        af_db = af
        af_norm = af_db - np.max(af_db)
        af_norm = np.clip(af_norm, -40, 0)
        self.ax.plot(theta, af_norm)
        self.ax.set_rticks(np.arange(np.floor(np.min(af_norm)), np.ceil(np.max(af_norm))+1, 10))
        self.ax.set_rlim(np.floor(np.min(af_norm)), np.ceil(np.max(af_norm)))
        self.ax.grid(True)
        self.ax.set_position([0.0, -0.3, 1, 1.6])

        self.canvas.draw()
