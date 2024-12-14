
import numpy as np
from PyQt5.QtWidgets import *


class FrequencyComponent:
    def __init__(self, frequency, phase_shift=0, amplitude=1.0):
        self.frequency = frequency
        self.phase_shift = phase_shift
        self.amplitude = amplitude

class ArrayElement:
    def __init__(self, position,phase_shift = 0, components=None , wave_type = 'acoustic'):
        self.position = np.array(position)
        self.phase_shift = phase_shift
        self.speed = 343.0 if wave_type == 'acoustic' else 300000000.0
        # Default to single 1kHz component if none provided
        self.components = components if components is not None else [FrequencyComponent(1000)]
        
    def add_frequency_component(self, frequency, phase_shift=0, amplitude=1.0):
        
        self.components.append(FrequencyComponent(frequency, phase_shift, amplitude))
    
    def remove_frequency_component(self, index): 
        self.components.pop(index)
        
    def calculate_field(self, point, time=0):
        distance = np.linalg.norm(point - self.position)
        total_field = 0
        
        for comp in self.components:
            k = 2 * np.pi * comp.frequency / self.speed
            total_field += comp.amplitude * np.exp(1j * (k * distance + comp.phase_shift))
            
        return total_field / max(distance, 0.1)