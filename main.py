import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from ArrayElement import ArrayElement
from Array import Array

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Array controls
        array_group = QGroupBox("Array Configuration")
        array_layout = QFormLayout()
        
        self.num_elements = QSpinBox()
        self.num_elements.setRange(2, 32)
        self.num_elements.setValue(8)
        array_layout.addRow("Number of Elements:", self.num_elements)
        
        self.geometry = QComboBox()
        self.geometry.addItems(['Linear', 'Curved'])
        array_layout.addRow("Geometry:", self.geometry)
        
        self.radius = QDoubleSpinBox()
        self.radius.setRange(0.1, 5.0)
        self.radius.setValue(1.0)
        self.radius.setSingleStep(0.1)
        array_layout.addRow("Radius (m):", self.radius)
        
        array_group.setLayout(array_layout)
        layout.addWidget(array_group)
        
        # Beam controls
        beam_group = QGroupBox("Beam Control")
        beam_layout = QFormLayout()
        
        self.steering = QSlider(Qt.Horizontal)
        self.steering.setRange(-90, 90)
        self.steering.setValue(0)
        beam_layout.addRow("Steering Angle (°):", self.steering)
        
        self.frequency = QSpinBox()
        self.frequency.setRange(100, 5000)
        self.frequency.setValue(1000)
        beam_layout.addRow("Frequency (Hz):", self.frequency)
        
        beam_group.setLayout(beam_layout)
        layout.addWidget(beam_group)
        
        # Add pattern selection
        pattern_group = QGroupBox("Element Pattern")
        pattern_layout = QVBoxLayout()
        
        self.pattern_type = QButtonGroup()
        self.isotropic_rb = QRadioButton("Isotropic")
        self.sinc_rb = QRadioButton("Sinc")
        self.isotropic_rb.setChecked(True)
        
        self.pattern_type.addButton(self.isotropic_rb)
        self.pattern_type.addButton(self.sinc_rb)
        pattern_layout.addWidget(self.isotropic_rb)
        pattern_layout.addWidget(self.sinc_rb)
        
        pattern_group.setLayout(pattern_layout)
        layout.addWidget(pattern_group)
        
        layout.addStretch()
        self.setLayout(layout)

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create figure with 2 subplots
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        # Create grid specification for custom layout
        gs = self.figure.add_gridspec(2, 1)
        
        # Create subplots
        self.ax_field = self.figure.add_subplot(gs[0])  # Top plot
        self.ax_polar = self.figure.add_subplot(gs[1], projection='polar')  # Bottom plot
        
        self.figure.tight_layout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def update_plots(self, arrays):
        self.ax_field.clear()
        self.ax_polar.clear()
        
        # Field plot
        x = np.linspace(-3, 3, 100) #100 points between -3 and 3
        y = np.linspace(-1, 5, 20)
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
        
        # Polar beam pattern plot
        theta = np.linspace(0, np.pi, 120)
        pattern = np.zeros_like(theta, dtype=complex)
        
        for array in arrays:
            r = 2.0
            for angle, i in zip(theta, range(len(theta))):
                point = r * np.array([np.cos(angle), np.sin(angle)])
                for element in array.elements:
                    pattern[i] += element.calculate_field(point)
        
        pattern_db = 20*np.log10(np.abs(pattern))
        pattern_db = np.maximum(pattern_db, -40)  # Limit minimum dB
        
        # Set counter-clockwise rotation
        self.ax_polar.plot(theta, pattern_db + 40)
        self.ax_polar.set_title('Polar Beam Pattern')
        self.ax_polar.set_theta_zero_location('E')  # 0° at East (right)
        self.ax_polar.set_theta_direction(1)  # Counter-clockwise direction
        self.ax_polar.set_rlabel_position(90)  # Move radial labels to top
        self.ax_polar.grid(True)
        
        # Set custom angle labels
        angles = np.arange(0, 360, 30)
        self.ax_polar.set_thetagrids(angles, labels=[f'{angle}°' for angle in angles])
        
        self.figure.tight_layout()
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beamforming Simulator")
        self.setup_ui()
        
        self.arrays = [Array()]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(100)
        
    def setup_ui(self):
        central = QWidget()
        layout = QHBoxLayout()
        
        self.controls = ControlPanel()
        self.plot_widget = PlotWidget()
        
        layout.addWidget(self.controls)
        layout.addWidget(self.plot_widget, stretch=2)
        
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        # Connect signals
        self.controls.num_elements.valueChanged.connect(self.update_array)
        self.controls.geometry.currentTextChanged.connect(self.update_array)
        self.controls.radius.valueChanged.connect(self.update_array)
        self.controls.steering.valueChanged.connect(self.update_array)
        self.controls.frequency.valueChanged.connect(self.update_array)
        
    def update_array(self):
        array = self.arrays[0]
        array.num_elements = self.controls.num_elements.value()
        array.geometry = self.controls.geometry.currentText().lower()
        array.radius = self.controls.radius.value()
        array.create_array()
        
        # Update frequency and steering
        freq = self.controls.frequency.value()
        pattern_type = 'isotropic' if self.controls.isotropic_rb.isChecked() else 'sinc'
        for element in array.elements:
            element.pattern_type = pattern_type
            element.frequency = freq
            
        array.set_steering_angle(self.controls.steering.value())
        
    def update_simulation(self):
        self.plot_widget.update_plots(self.arrays)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())