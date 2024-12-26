

import numpy as np
from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from Array import Array

class FieldPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.color = np.random.rand(3,)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax_field = self.figure.add_subplot(111)
        self.figure.tight_layout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def update_plot(self, arrays:list[Array],extent = [-15, 15, 0, 10]):
        if len(arrays) == 0:
            #remove plot
            self.ax_field.clear()
            self.figure.clear()
            self.canvas.draw()
            return
        x = np.linspace(-15, 15, 200)
        y = np.linspace(0, 10, 200)
        field = arrays[0].calculate_field(x,y)
        for i, array in enumerate(arrays[1:], 1):
            field += array.calculate_field(x,y)
        # Normalize field to be above 0
        field = field - np.min(field)

        self.ax_field.clear()
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        im = self.ax.imshow(field, extent=extent, aspect='equal', 
                    cmap='jet', origin='lower')
        self.figure.colorbar(im, ax=self.ax, orientation='vertical', fraction=0.046, pad=0.04,shrink=0.8)
        self.ax.set_xlabel('x (m)')
        self.ax.set_ylabel('y (m)')
        self.ax.set_position([0.0, 0.1, 0.9, 0.8])
        self.canvas.draw()

    def plot_target_point(self,x,y):
        if x > 6 or x < -6 or y > 10 or y < 0:
            return
        self.ax.plot(x, y, 'g*', markersize=15, label='Target Point')
        self.ax.legend()
        self.canvas.draw()