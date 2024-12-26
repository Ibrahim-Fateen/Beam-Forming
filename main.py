import json
import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog
from Array import Array, FrequencyComponent

from mainwin import Ui_MainWindow
from InterferenceMap import FieldPlotWidget
from BeamPattern import PolarPlotWidget
import os
import logging
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Create logger instance
logger = logging.getLogger('beam_forming')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_plots()
        self.setup_controls()
        self.block = False
        self.arrays:list[Array] = []
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_simulation)
        # self.timer.start(100)

    def setup_plots(self):
        logger.info('Setting up plots...')
        self.polar_plot = PolarPlotWidget()
        beam_layout = QVBoxLayout(self.ui.BeamProfile)
        beam_layout.addWidget(self.polar_plot)
        beam_layout.setContentsMargins(0, -5, 0, -5)
        self.field_plot = FieldPlotWidget()
        interference_layout = QVBoxLayout(self.ui.InterferenceMap)
        interference_layout.addWidget(self.field_plot)
        interference_layout.setContentsMargins(0, 0, 0, 0)
    def setup_controls(self):
        logger.info('Setting up controls...')
        self.ui.addArrayButton.clicked.connect(self.add_array)
        self.ui.removeArrayButton.clicked.connect(self.remove_array)
        self.ui.arrayList.currentRowChanged.connect(lambda index: self.on_array_selected(index))

        self.ui.xPosition.valueChanged.connect(self.update_selected_array)
        self.ui.yPosition.valueChanged.connect(self.update_selected_array)
        self.ui.rotation.valueChanged.connect(self.update_selected_array)
        self.ui.numElements.valueChanged.connect(self.update_selected_array)
        self.ui.elementSpacing.valueChanged.connect(self.update_selected_array)
        self.ui.curvature.valueChanged.connect(self.update_selected_array)
        self.ui.steeringAngle.valueChanged.connect(self.update_selected_array)
        self.ui.follow_target_checkBox.stateChanged.connect(self.update_simulation)
        self.ui.xPosition_target.valueChanged.connect(self.update_simulation)
        self.ui.yPosition_target.valueChanged.connect(self.update_simulation)
        self.ui.addFrequencyButton.clicked.connect(self.add_frequency)
        self.ui.removeFrequencyButton.clicked.connect(self.remove_frequency)
        # self.ui.plotTabs.currentChanged.connect(self.update_simulation)
        self.ui.comboBox.currentIndexChanged.connect(self.update_selected_array)
        self.ui.rotation.valueChanged.connect(self.update_selected_array)
        self.ui.comboBox_2.addItems(['Hz', 'kHz', 'MHz'])

        self.ui.saveScenarioButton.clicked.connect(self.save_scenario)
        self.ui.loadScenarioButton.clicked.connect(self.load_scenario_from_device)

        self.ui.scenarioSelect.activated.connect(self.load_selected_scenario)
        self.ui.frequencyInput.valueChanged.connect(self.update_selected_frequency)
        self.ui.phaseInput.valueChanged.connect(self.update_selected_frequency)
        self.ui.amplitudeInput.valueChanged.connect(self.update_selected_frequency)
        self.ui.frequencyList.currentRowChanged.connect(self.update_selected_frequency_ui)
        self.ui.comboBox_2.currentIndexChanged.connect(self.update_selected_frequency)
        # self.ui.frequencyList.currentRowChanged.connect(self.update_selected_frequency)

        self.populate_scenario_select()

    def save_scenario(self):
        try:
            logger.info('Saving scenario...')
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Scenario", "scenarios/",
                                                       "JSON Files (*.json);;All Files (*)", options=options)
            if file_name:
                scenario = {
                    "arrays": [
                        {
                            "center": array.center.tolist(),
                            "num_elements": array.num_elements,
                            "spacing": array.spacing,
                            "curvature": array.curvature,
                            "rotation": array.rotation,
                            "steering_angle": array.steering_angle,
                            "type": array.type,
                            "frequencies": [
                                {
                                 "frequency":comp.frequency,
                                 "phase":comp.phase,
                                 "amplitude":comp.amplitude
                                } 
                                for comp in array.components
                            ]
                        }
                        for array in self.arrays
                    ],
                    "target": {
                        "x": self.ui.xPosition_target.value(),
                        "y": self.ui.yPosition_target.value()
                    },
                    "follow_target": self.ui.follow_target_checkBox.isChecked()
                }
                with open(file_name, 'w') as file:
                    json.dump(scenario, file, indent=4)
                # print("Scenario saved successfully.")
                self.populate_scenario_select()
        except Exception as e:
            logger.error(f"An error occurred while saving the scenario: {e}")
            print(f"An error occurred while saving the scenario: {e}")

    def load_scenario_from_device(self):
        logger.info('Loading scenario...')
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Scenario", "", "JSON Files (*.json);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, 'r') as file:
                scenario = json.load(file)
                self.arrays.clear()
                self.ui.arrayList.clear()
                for array_data in scenario["arrays"]:
                    array = Array(
                        center=array_data["center"],
                        num_elements=array_data["num_elements"],
                        spacing=array_data["spacing"],
                        curvature=array_data["curvature"],
                        rotation=array_data["rotation"],
                        type=array_data["type"]
                    )
                    array.set_steering_angle(array_data["steering_angle"])
                    components = [FrequencyComponent(**comp) for comp in array_data["frequencies"]]
                    array.components = components
                    self.arrays.append(array)
                    self.ui.arrayList.addItem(f"Array {len(self.arrays)}")
                if self.arrays:
                    self.ui.arrayList.setCurrentRow(0)
                self.ui.xPosition_target.setValue(scenario["target"]["x"])
                self.ui.yPosition_target.setValue(scenario["target"]["y"])
                self.ui.follow_target_checkBox.setChecked(scenario["follow_target"])
                self.update_selected_array()

    def load_selected_scenario(self, index):
        logger.info('Loading selected scenario...')
        file_name = self.ui.scenarioSelect.currentText()
        if file_name:
            file_path = os.path.join("scenarios", file_name)
            with open(file_path, 'r') as file:
                scenario = json.load(file)
                self.arrays.clear()
                self.ui.arrayList.clear()
                for array_data in scenario["arrays"]:
                    array = Array(
                        center=array_data["center"],
                        num_elements=array_data["num_elements"],
                        spacing=array_data["spacing"],
                        curvature=array_data["curvature"],
                        rotation=array_data["rotation"],
                        type=array_data["type"]
                    )
                    array.set_steering_angle(array_data["steering_angle"])
                    components = [FrequencyComponent(**comp) for comp in array_data["frequencies"]]
                    array.components = components
                    self.arrays.append(array)
                    self.ui.arrayList.addItem(f"Array {len(self.arrays)}")
                if self.arrays:
                    self.ui.arrayList.setCurrentRow(0)
                self.ui.xPosition_target.setValue(scenario["target"]["x"])
                self.ui.yPosition_target.setValue(scenario["target"]["y"])
                self.ui.follow_target_checkBox.setChecked(scenario["follow_target"])
                self.update_selected_array()

    def populate_scenario_select(self):
        logger.info('Populating scenario select...')
        current_selection = self.ui.scenarioSelect.currentText()
        self.ui.scenarioSelect.blockSignals(True)
        self.ui.scenarioSelect.clear()
        scenario_dir = "scenarios"  # Directory where scenarios are saved
        if not os.path.exists(scenario_dir):
            os.makedirs(scenario_dir)
        for file_name in os.listdir(scenario_dir):
            if file_name.endswith(".json"):
                self.ui.scenarioSelect.addItem(file_name)
        if current_selection:
            index = self.ui.scenarioSelect.findText(current_selection)
            if index != -1:
                self.ui.scenarioSelect.setCurrentIndex(index)
        self.ui.scenarioSelect.blockSignals(False)

    def add_array(self):
        logger.info('Adding array...')
        array = Array()
        self.arrays.append(array)
        name = f"Array {len(self.arrays)}"
        if self.ui.arrayList.count() == 0:
            name = "Array 1"
        else:
            last_array_name = self.ui.arrayList.item(len(self.arrays) - 2).text()
            last_array_number = int(last_array_name.split(" ")[1])
            name = f"Array {last_array_number + 1}"
        self.ui.arrayList.addItem(name)
        if len(self.arrays) == 1:
            self.ui.arrayList.setCurrentRow(0)
        self.update_selected_array()

    def remove_array(self):
        logger.info('Removing array...')
        current_row = self.ui.arrayList.currentRow()
        if current_row >= 0:
            self.arrays.pop(current_row)
            self.ui.arrayList.takeItem(current_row)
            self.update_simulation()
    
    def on_array_selected(self, index):
        logger.info(f'Array of index {index} selected...')
        self.block = True
        if index >= 0 and index < len(self.arrays):
            # print(index)
            array = self.arrays[index]
            self.ui.steeringAngle.setValue(int(array.steering_angle))
            self.ui.numElements.setValue(array.num_elements)
            self.ui.elementSpacing.setValue(array.spacing)
            self.ui.curvature.setValue(array.curvature)
            self.ui.xPosition.setValue(array.center[0])
            self.ui.yPosition.setValue(array.center[1])
            self.ui.rotation.setValue(int(array.rotation))
            self.ui.steeringValue.setText(f"{array.steering_angle}")
            self.ui.comboBox.setCurrentIndex(0 if array.type == 'acoustic' else 1)
            
        self.block = False
        self.update_simulation()


    def add_frequency(self):
        logger.info('Adding frequency...')
        freq = self.ui.frequencyInput.value()
        unit = self.ui.comboBox_2.currentText()
        if unit == 'kHz':
            freq *= 1000
        elif unit == 'MHz':
            freq *= 1000000
        phase = self.ui.phaseInput.value()
        amplitude = self.ui.amplitudeInput.value()
        current_row = self.ui.arrayList.currentRow()
        if current_row >= 0 and current_row < len(self.arrays):
            array:Array = self.arrays[current_row]
            self.block = True
            temp = self.ui.steeringAngle.value()
            array.set_steering_angle(0)
            array.add_frequency_component(freq, phase, amplitude)
            array.set_steering_angle(temp)
            self.block = False
            self.update_simulation()
    def update_selected_frequency(self):
        if self.block:
            return
        self.block = True
        current_row = self.ui.frequencyList.currentRow()
        if current_row >= 0:
            current_array = self.ui.arrayList.currentRow()
            if current_array >= 0 and current_array < len(self.arrays):
                array = self.arrays[current_array]
                comp = array.components[current_row]
                unit = self.ui.comboBox_2.currentText()
                if unit == 'kHz':
                    comp.frequency = self.ui.frequencyInput.value() * 1000
                elif unit == 'MHz':
                    comp.frequency = self.ui.frequencyInput.value() * 1000000
                else:
                    comp.frequency = self.ui.frequencyInput.value()
                comp.phase = self.ui.phaseInput.value()
                comp.amplitude = self.ui.amplitudeInput.value()
                self.update_simulation()
    def update_selected_frequency_ui(self):
        self.block = True
        current_row = self.ui.frequencyList.currentRow()
        if current_row >= 0:
            current_array = self.ui.arrayList.currentRow()
            if current_array >= 0 and current_array < len(self.arrays):
                array = self.arrays[current_array]
                comp = array.components[current_row]
                # check unit 
                comp_freq = comp.frequency
                if comp_freq >= 1000000:
                    self.ui.comboBox_2.setCurrentIndex(2)
                    comp_freq /= 1000000
                elif comp_freq >= 1000:
                    self.ui.comboBox_2.setCurrentIndex(1)
                    comp_freq /= 1000
                else:
                    self.ui.comboBox_2.setCurrentIndex(0)
                self.ui.frequencyInput.setValue(int(comp_freq))
                self.ui.phaseInput.setValue(comp.phase)
                self.ui.amplitudeInput.setValue(int(comp.amplitude))
        self.block = False

    def remove_frequency(self):
        logger.info('Removing frequency...')
        current_row = self.ui.frequencyList.currentRow()
        if current_row >= 0:
            current_array = self.ui.arrayList.currentRow()
            if current_array >= 0 and current_array < len(self.arrays):
                array = self.arrays[current_array]
                array.remove_frequency_component(current_row)
                self.update_simulation()

    def update_selected_array(self):
        if self.block:
            return
        current_row = self.ui.arrayList.currentRow()
        if current_row >= 0 and current_row < len(self.arrays):
            array = self.arrays[current_row]
            array.num_elements = self.ui.numElements.value()
            array.spacing = self.ui.elementSpacing.value()
            array.curvature = self.ui.curvature.value()
            
            array.center = np.array([self.ui.xPosition.value(), self.ui.yPosition.value()])
            array.rotation = self.ui.rotation.value()
            array.type = self.ui.comboBox.currentText().lower()
            array.c = 343.0 if array.type == 'acoustic' else 300000000.0
            # array.update_elements_postion()
            array.set_steering_angle(self.ui.steeringAngle.value())
            self.ui.steeringValue.setText(f"{array.steering_angle}")
            self.ui.rotationValue.setText(f"{array.rotation}")
            self.update_simulation()

    def update_simulation(self):
        # logger.info('Updating simulation...')
        selected_array = self.ui.arrayList.currentRow()
        self.block = True
        if self.ui.follow_target_checkBox.isChecked():
            self.ui.xPosition_target.setDisabled(False)
            self.ui.yPosition_target.setDisabled(False)
            for array in self.arrays:
                array.set_steering_target(targetx=self.ui.xPosition_target.value(), targety=self.ui.yPosition_target.value())
            self.ui.steeringAngle.setDisabled(True)
        else:
            self.ui.xPosition_target.setDisabled(True)
            self.ui.yPosition_target.setDisabled(True)
            self.ui.steeringAngle.setDisabled(False)
            if selected_array >= 0 and selected_array < len(self.arrays):
                array = self.arrays[selected_array]
                array.set_steering_angle(self.ui.steeringAngle.value())
        
        self.field_plot.update_plot(self.arrays)
        if self.ui.follow_target_checkBox.isChecked():
            self.field_plot.plot_target_point(self.ui.xPosition_target.value(), self.ui.yPosition_target.value())
        if selected_array >= 0 and selected_array < len(self.arrays):
            self.polar_plot.update_plot(self.arrays[selected_array])
        current_index = self.ui.frequencyList.currentRow()
        self.ui.frequencyList.clear()
        current_row = self.ui.arrayList.currentRow()
        if current_row >= 0 and current_row < len(self.arrays):
            array = self.arrays[current_row]
            for comp in array.components:
                amplitude = comp.amplitude
                frequency = comp.frequency
                phase = comp.phase
                equation = f"{amplitude:.2f}*sin(2π*{frequency}t + {phase:.2f}°)"
                self.ui.frequencyList.addItem(equation)
            if current_index >= 0 and current_index < len(array.components):
                comp = array.components[current_index]

                self.ui.frequencyList.setCurrentRow(current_index)
        if len(self.arrays) == 0:return
        self.block = False
        array:Array = self.arrays[0 if len(self.arrays) == selected_array else selected_array]
        logger.info(f"Selected array data:\n"
               f"Center: {array.center}\n"
               f"Number of elements: {array.num_elements}\n"
               f"Spacing: {array.spacing}\n"
               f"Curvature: {array.curvature}\n"
               f"Rotation: {array.rotation}\n"
               f"Steering angle: {array.steering_angle}\n"
               f"Array speed: {array.c}")
  


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())