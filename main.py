import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from Array import Array
from mainwin import Ui_MainWindow
from InterferenceMap import FieldPlotWidget
from BeamPattern import PolarPlotWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_plots()
        self.setup_controls()
        
        self.arrays = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(100)

    def setup_plots(self):
        self.field_plot = FieldPlotWidget()
        beam_layout = QVBoxLayout(self.ui.beamPatternTab)
        beam_layout.addWidget(self.field_plot)

        self.polar_plot = PolarPlotWidget()
        interference_layout = QVBoxLayout(self.ui.interferenceMapTab)
        interference_layout.addWidget(self.polar_plot)

    def setup_controls(self):
        self.ui.addArrayButton.clicked.connect(self.add_array)
        self.ui.removeArrayButton.clicked.connect(self.remove_array)
        self.ui.arrayList.currentRowChanged.connect(self.on_array_selected)

        self.ui.xPosition.valueChanged.connect(self.update_selected_array)
        self.ui.yPosition.valueChanged.connect(self.update_selected_array)
        self.ui.rotation.valueChanged.connect(self.update_selected_array)
        self.ui.numElements.valueChanged.connect(self.update_selected_array)
        self.ui.elementSpacing.valueChanged.connect(self.update_selected_array)
        self.ui.curvature.valueChanged.connect(self.update_selected_array)
        self.ui.steeringAngle.valueChanged.connect(self.update_selected_array)

        self.ui.addFrequencyButton.clicked.connect(self.add_frequency)
        self.ui.removeFrequencyButton.clicked.connect(self.remove_frequency)

        self.ui.comboBox_2.addItems(['Hz', 'kHz', 'MHz'])

    def add_array(self):
        array = Array()
        self.arrays.append(array)
        self.ui.arrayList.addItem(f"Array {len(self.arrays)}")
        if len(self.arrays) == 1:
            self.ui.arrayList.setCurrentRow(0)

    def remove_array(self):
        current_row = self.ui.arrayList.currentRow()
        if current_row >= 0:
            self.arrays.pop(current_row)
            self.ui.arrayList.takeItem(current_row)

    def on_array_selected(self, index):
        if index >= 0 and index < len(self.arrays):
            array = self.arrays[index]
            self.ui.numElements.setValue(array.num_elements)
            self.ui.elementSpacing.setValue(array.radius / max(1, array.num_elements - 1))
            self.ui.curvature.setValue(array.curvature)

    def add_frequency(self):
        freq = self.ui.frequencyInput.value()
        unit = self.ui.comboBox_2.currentText()
        if unit == 'kHz':
            freq *= 1000
        elif unit == 'MHz':
            freq *= 1000000
        self.ui.frequencyList.addItem(f"{freq} Hz")

    def remove_frequency(self):
        current_row = self.ui.frequencyList.currentRow()
        if current_row >= 0:
            self.ui.frequencyList.takeItem(current_row)

    def update_selected_array(self):
        current_row = self.ui.arrayList.currentRow()
        if current_row >= 0 and current_row < len(self.arrays):
            array = self.arrays[current_row]
            array.num_elements = self.ui.numElements.value()
            array.radius = self.ui.elementSpacing.value() * (array.num_elements - 1)
            array.curvature = self.ui.curvature.value()
            
            array.center = np.array([self.ui.xPosition.value(), self.ui.yPosition.value()])
            array.rotation = self.ui.rotation.value()
            
            array.create_array()
            array.set_steering_angle(self.ui.steeringAngle.value())

            freqs = []
            for i in range(self.ui.frequencyList.count()):
                freq_text = self.ui.frequencyList.item(i).text()
                freq = float(freq_text.split()[0])
                freqs.append(freq)
            
            if freqs:
                for element in array.elements:
                    element.frequencies = freqs

    def update_simulation(self):
        self.field_plot.update_plot(self.arrays)
        self.polar_plot.update_plot(self.arrays)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())