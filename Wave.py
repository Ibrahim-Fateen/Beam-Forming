from typing import List

class Wave:
    """
    Wave Equation: u(x,t)= A*sin(kx-wt+phi)\n
    u = Vertical Displacement, A = Amplitude, x = distance covered by wave, w = angular frequency, phi = phase\n
    k is the wave number, k = 2*pi / lambda where lambda is the wavelength\n 
    A wave is composed of multiple components \n
    Each component is a wave with amplitude, frequency and phase\n
    Frequencies are in rad/sec
    """
    def __init__(self):
        self.components: List[WaveComponent] = []
        
    def add_component(self, amplitude, frequency, phase):
        component = WaveComponent(amplitude, frequency, phase)
        self.components.append(component)
        
    def remove_component(self, amplitude, frequency, phase):
        for component in self.components:
            if amplitude==component.amplitude:
                if frequency==component.frequency:
                    if phase==component.phase:
                        self.components.remove(component)    
    
class WaveComponent:
    def __init__(self, amplitude, frequency, phase):
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase
        
    _