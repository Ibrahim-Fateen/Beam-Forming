import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Wave import EM_Wave
from typing import List

PI = np.pi    
class Array:
    """
A an array of N linear Isotropic elements spaced by S.\n
Array Pattern = Array Factor * Element Pattern.\n
Isotropic Element Pattern = 1\n
Steering Angle should be provided in degrees   
    """
    def __init__(self, wave:EM_Wave, N:int = 4, S:float = 0.5, steering_angle:float=90):
        self.N = N
        self.S = S
        self.wave = wave
        self.steering_angle = steering_angle
        self.phase_vector = self.calc_phase_vector()
        self.array_factor = self.calc_array_factor()        
        self.beam_pattern = np.abs(self.array_factor)
        
    def calc_array_factor(self):
        """
    Array factor is a complex number and its magnitude is the beam Pattern\n
    General Array Factor Equation: SIGMA[0 -> N-1]
    (e^j(phi + k*S*n*cos(theta)))\n
    n = index of the curr element\n
    phi = the applied phase for current element\n
    K = wave number\n
    S = Spacing between each two elements\n
    theta = steering angle measured from the +ve x-axis
        """
        array_factor = np.zeros(self.N, dtype=complex)
        
        for n in range(self.N):
           phi_n = self.phase_vector[n]
           K = self.wave.wave_number
           S = self.S
           theta_rad = self.steering_angle * PI / 180
           array_factor[n] = np.exp(1j*(phi_n + K*S*n*np.cos(theta_rad)))
           
        return np.sum(array_factor)    
    
    def calc_phase_vector(self):
        phase_vector = []
        steering_angle_rad = self.steering_angle * PI / 180
        delta_phase = self.wave.wave_number * self.S * np.sin(steering_angle_rad)
        
        for i in range(self.N):
            phase_vector.append(i*delta_phase)
            
        return phase_vector      

    