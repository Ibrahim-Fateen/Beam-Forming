from typing import List
import numpy as np

PI = np.pi
C = 3 * (10^8)

class EM_Wave:
    """
An Electromagnetice Wave is composed of two fields.\n
For beam forming simulators, only the electric field wave is considered.\n
Frequency is measured in GHZ.\n
C (Wave Speed)= 3 * 10^8
    """
    def __init__(self, amplitude:float=1, wave_length=2*PI):
        self.amplitude = amplitude
        self.wave_length = wave_length
        self.wave_number = 2*PI / wave_length
        self.frequency = C / wave_length
        self.components: List[EM_Wave] = []
        self.speed = C
        
    
    def add_component(self, amplitude, frequency):
        component = EM_Wave(amplitude, frequency)
        self.components.append(component)
        
    def remove_component(self, amplitude, frequency, phase):
        for component in self.components:
            if amplitude==component.amplitude and frequency==component.frequency:
                self.components.remove(component)    
       