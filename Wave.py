from typing import List
import numpy as np

PI = np.pi

class Speeds:
    def __init__(self):
        # Speeds are defined in m/s
        self.C = 3 * (10^8) #Speed of light
        self.V_Longitudinal_Air = 343
        self.V_Longitudinal_Water = 1480
        self.V_Longitudinal_Lungs = 330
        self.V_Longitudinal_Soft_Tissue = 1540
        self.V_Longitudinal_Bones = 3500
        self.V_Longitudinal_Cartialge = 1700

class EM_Wave:
    """
Wave Speed = 3*(10^8)
Frequency of an Electromagnetic Wave is measured in GHZ.\n
    """
    def __init__(self, amplitude:float=1, frequency=10^9):
        self.speeds = Speeds()
        
        self.speed = self.speeds.C
        self.amplitude = amplitude
        self.frequency = frequency
        self.wave_length = self.speed / self.frequency
        self.wave_number = 2*PI / self.wave_length
        self.components: List[EM_Wave] = []
        
    
    def add_component(self, amplitude, frequency):
        component = EM_Wave(amplitude, frequency)
        self.components.append(component)
        
    def remove_component(self, amplitude, frequency, phase):
        for component in self.components:
            if amplitude==component.amplitude and frequency==component.frequency:
                self.components.remove(component)    

class Acoustic_Wave:
    """
Acoustive waves are classified into longitudinal, transverse and surface waves.\n
Longitudinal can travel through solids and fluids while transverse can travel trhough solids only.\n
The speed of an acoustice wave is constant per medium.\n
v = sqrt(M / rho) where is the modulus of the medium and rho is the medium density\n
For longitudinal waves, M is Y(Young Modulus) for solids or B(Bulk Modulus) for fluids.\n
For Transvers waves M = G (Shear Modulus).\n
Longitudinal waves are the most used with phased arrays for their high flexibility.    
    """
    def __init__(self, frequency:float, amplitude=1, medium:str="air", type="longitudinal"):
        self.speeds = Speeds()
        
        self.amplitude = amplitude
        self.medium = medium
        
        #speed in m/s and freqency in HZ
        self.speed, self.frequency_range = self.calc_speed_and_frequency_range_based_on_medium()
        
        if not (frequency>=self.frequency_range[0] and frequency<=self.frequency_range[1]):
            print("invalid frequency range")
            return
        
        self.frequency = frequency
        self.wavelength = self.speed / self.frequency
        self.wave_number = 2*np.pi / self.wavelength
        self.components: List[Acoustic_Wave] = [ ]
        
    def calc_speed_and_frequency_range_based_on_medium(self):
        if self.medium == "air":
            speed = self.speeds.V_Longitudinal_Air
            frequency_range = [200, 20000]
                   
        elif self.medium == "water":
            speed = self.speeds.V_Longitudinal_Water
            frequency_range = [100000, 1000000]
        
        elif self.medium == "soft tissue":
            speed=self.speeds.V_Longitudinal_Lungs
            frequency_range = [10^6, 15*(10^6)]
            
        elif self.medium == "bones":
            speed = self.speeds.V_Longitudinal_Bones
            frequency_range = [10^6, 10 * (10^6)]
            
        elif self.medium == "cartilage":
            speed = self.speeds.V_Longitudinal_Cartialge
            frequency_range = [1.7*(10^6), 17*(10^6)]
            
        elif self.medium == "lungs":
            speed = self.speeds.V_Longitudinal_Lungs
            frequency_range = [2 * (10^6), 15*(10^6)]            
        
        return speed, frequency_range
    
    def add_component(self, amplitude, frequency):
        component = EM_Wave(amplitude, frequency)
        self.components.append(component)
        
    def remove_component(self, amplitude, frequency, phase):
        for component in self.components:
            if amplitude==component.amplitude and frequency==component.frequency:
                self.components.remove(component)           