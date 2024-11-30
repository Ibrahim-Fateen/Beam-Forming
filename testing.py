import sys
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QPushButton, QComboBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class BeamProfileViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.ax = self.canvas.figure.subplots()

    def plot_beam_profile(self, data):
        """Plot the beam profile data."""
        self.ax.clear()
        self.ax.plot(data['angles'], data['intensities'], label="Beam Profile")
        self.ax.set_xlabel("Angle (degrees)")
        self.ax.set_ylabel("Intensity")
        self.ax.set_title("Beam Profile")
        self.ax.legend()
        self.canvas.draw()


class InterferenceMapViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.ax = self.canvas.figure.subplots()
        self.colorbar = None

    def plot_interference_map(self, interference_data):
        """Plot the interference map data."""
        self.ax.clear()
        im = self.ax.imshow(interference_data, cmap='viridis', origin='lower')
        self.ax.set_title("Constructive/Destructive Interference Map")
        self.ax.set_xlabel("X Position")
        self.ax.set_ylabel("Y Position")

        # Remove the previous colorbar if it exists
        if self.colorbar:
            self.colorbar.remove()

        # Add a new colorbar
        self.colorbar = self.canvas.figure.colorbar(im, ax=self.ax)
        self.canvas.draw()

class MainBeamformingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beamforming Simulator")
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Add visualization components
        self.beam_viewer = BeamProfileViewer()
        self.interference_viewer = InterferenceMapViewer()

        layout.addWidget(self.beam_viewer)
        layout.addWidget(self.interference_viewer)

        # Add parameter controls
        control_layout = QHBoxLayout()
        self.num_transmitters_slider = self.create_slider("Num Transmitters", 1, 100, 10)
        self.frequency_selector = self.create_dropdown("Frequency", [1e9, 2e9, 5e9])
        self.array_geometry_selector = self.create_dropdown("Geometry", ["Linear", "Curved"])

        control_layout.addWidget(self.num_transmitters_slider)
        control_layout.addWidget(self.frequency_selector)
        control_layout.addWidget(self.array_geometry_selector)

        layout.addLayout(control_layout)
        self.setCentralWidget(central_widget)

        # Connect controls to visualization updates
        self.num_transmitters_slider.findChild(QSlider).valueChanged.connect(self.update_visualizations)
        self.frequency_selector.findChild(QComboBox).currentIndexChanged.connect(self.update_visualizations)
        self.array_geometry_selector.findChild(QComboBox).currentIndexChanged.connect(self.update_visualizations)

    def create_slider(self, label, min_val, max_val, default):
        """Create a labeled slider."""
        container = QWidget()
        layout = QVBoxLayout(container)
        label_widget = QLabel(label)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default)
        layout.addWidget(label_widget)
        layout.addWidget(slider)
        return container

    def create_dropdown(self, label, options):
        """Create a labeled dropdown."""
        container = QWidget()
        layout = QVBoxLayout(container)
        label_widget = QLabel(label)
        dropdown = QComboBox()
        for option in options:
            dropdown.addItem(str(option))
        layout.addWidget(label_widget)
        layout.addWidget(dropdown)
        return container

    def update_visualizations(self):
        """Update visualizations based on parameter changes."""
        num_transmitters = self.num_transmitters_slider.findChild(QSlider).value()
        frequency = float(self.frequency_selector.findChild(QComboBox).currentText())
        geometry = self.array_geometry_selector.findChild(QComboBox).currentText()

        # Example data for visualization
        beam_profile_data = {
            "angles": np.linspace(-90, 90, 181),
            "intensities": np.sin(np.radians(np.linspace(-90, 90, 181))) ** 2 * num_transmitters,
        }
        interference_data = np.random.random((100, 100))  # Replace with real calculations

        self.beam_viewer.plot_beam_profile(beam_profile_data)
        self.interference_viewer.plot_interference_map(interference_data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainBeamformingApp()
    main_window.show()
    sys.exit(app.exec())