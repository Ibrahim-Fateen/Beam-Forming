import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Wave import EM_Wave
from typing import List
from scipy.integrate import quad

PI = np.pi    
class Array:
    """
A an array of N linear Isotropic elements spaced by distance S.
S is a function of the wavelength of the emitted wave. It should be a factor the wavelength\n
Array Pattern = Array Factor * Element Pattern.\n
Steering Angle should be provided in degrees.\n
Integration max subdivisions number controls the perfromance of the integration process to calculate the beam pattern 
over the semi circle. A higher number means better accuracy but more computation power.   
    """
    def __init__(self, wave:EM_Wave, S:float=0.5, N:int = 8, steering_angle:float=90, integration_max_subdivisions:int=150):
        self.N = N
        self.wave = wave
        self.S = S * self.wave.wave_length
        self.steering_angle = steering_angle
        self.integration_max_subdivisions = integration_max_subdivisions
        self.beam_pattern, self.integration_error = self.calc_beam_pattern()
               
        
    def calc_inst_beam_pattern(self, theta_obs):
        """
General Instantenous Array Factor Formula: e^( jKSN * [cos(theta_obs)-sin(theta_steer)] )\n
Beam Pattern = |Array Factor|       
        """
        array_factor_vector = np.zeros(self.N, dtype=complex)
        steer_angle_rad = np.radians(self.steering_angle)
        K = self.wave.wave_number
        theta_obs_rad = np.radians(theta_obs)
        
        for n in range(self.N):
           array_factor_vector[n] =self.wave.amplitude* np.exp(1j* K* self.S* n* (np.cos(theta_obs_rad) - np.sin(steer_angle_rad)))
        
        array_factor = np.sum(array_factor_vector)  
        inst_beam_pattern = np.abs(array_factor)
        
        return inst_beam_pattern
        
    def calc_beam_pattern(self):
        def integrand(theta_obs):
            return self.calc_inst_beam_pattern(theta_obs)
        
        beam_pattern, integration_err =quad(integrand, a=0, b=180, limit=self.integration_max_subdivisions)
        return beam_pattern, integration_err 
    