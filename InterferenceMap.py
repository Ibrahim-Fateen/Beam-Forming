

import numpy as np
from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class FieldPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax_field = self.figure.add_subplot(111)
        self.figure.tight_layout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def update_plot(self, arrays):
        self.ax_field.clear()
        
        # Field plot
        x = np.linspace(-3, 3, 10)
        y = np.linspace(-1, 3, 10)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X, dtype=complex)
        
        for array in arrays:
            for element in array.elements:
                points = np.stack([X.flatten(), Y.flatten()], axis=1)
                field = np.array([element.calculate_field(point) for point in points])
                Z += field.reshape(X.shape)
                
        self.ax_field.contourf(X, Y, np.abs(Z), levels=50)
        self.ax_field.set_title('Field Intensity')
        self.ax_field.set_aspect('equal')
        self.figure.tight_layout()
        self.canvas.draw()