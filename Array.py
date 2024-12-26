
import numpy as np
from PyQt5.QtWidgets import *

class FrequencyComponent:
    def __init__(self, frequency=1000, phase=0, amplitude=1.0):
        self.frequency = frequency  # Hz
        self.phase = phase  # radians
        self.amplitude = amplitude

class Array:
    def __init__(self, num_elements=8, spacing=0.2,center=(0,0) ,curvature=0.0, rotation=0.0, components=None,type = 'acoustic'):
        self.num_elements = num_elements
        self.spacing = spacing  # wavelengths
        self.steering_angle = 0  # degrees
        self.components = components if components is not None else [FrequencyComponent()]
        self.center = np.array(center)
        self.curvature = curvature
        self.rotation = rotation
        self.type = type
        self.c = 343.0 if type == 'acoustic' else 300000000.0
    def add_frequency_component(self, frequency, phase=0, amplitude=1.0):
        self.components.append(FrequencyComponent(frequency, phase, amplitude))
    def remove_frequency_component(self, index):
        self.components.pop(index)
    def change_speed(self, type):
        self.c = 343.0 if type == 'acoustic' else 300000000.0
        self.type = type
    def set_steering_angle(self, angle):
        self.steering_angle = angle

    def set_steering_target(self, targetx, targety):
        angle = np.degrees(np.arctan2(targety-self.center[1],targetx-self.center[0]))
        angle -= 90
        angle *= -1
        self.steering_angle = angle 
        print(f"target degree : {self.steering_angle}")
    def calculate_beam_pattern(self, theta):
        af = np.zeros_like(theta, dtype=complex)
        for comp in self.components:
            k = 2 * np.pi * comp.frequency / self.c
            wavelength = self.c / comp.frequency
            d = self.spacing   # spacing in meters
            psi = k * d * (np.cos(theta) - np.sin(np.radians(self.steering_angle)))
            component_af = np.zeros_like(theta, dtype=complex)
            for n in range(self.num_elements):
                component_af += comp.amplitude * np.exp(1j * (n * psi + comp.phase))
            af += component_af
        return 20 * np.log10(np.abs(af) / self.num_elements)

    def calculate_field(self, x, y, is_decayed=True):
        field = np.zeros((len(y), len(x)), dtype=complex)
        if len(self.components) == 0:
            return np.abs(field)
        for comp in self.components:
            k = 2 * np.pi * comp.frequency / self.c
            wavelength = self.c / comp.frequency
            component_field = np.zeros_like(field)
            # Calculate element positions considering center, curvature and rotation
            for n in range(self.num_elements):
                d = self.spacing  
                # Base position relative to center
                x_offset = (n - (self.num_elements - 1)/2) * d
                y_offset = self.curvature * x_offset**2  # Apply curvature
                # Apply rotation
                rot_angle = np.radians(self.rotation)
                x_n = self.center[0] + x_offset * np.cos(rot_angle) - y_offset * np.sin(rot_angle)
                y_n = self.center[1] + x_offset * np.sin(rot_angle) + y_offset * np.cos(rot_angle)
                X, Y = np.meshgrid(x - x_n, y - y_n)
                R = np.sqrt(X**2 + Y**2)
                phase = (k * R + 
                        n * k * d * np.sin(np.radians(self.steering_angle)) +
                        comp.phase)
                attenuation = 1.0 / (R + np.finfo(float).eps)  # Geometric spreading
                frequency_attenuation = np.exp(-comp.frequency * R / (1e6 * self.c))  # Frequency-dependent attenuation
                component_field += comp.amplitude * attenuation * frequency_attenuation * np.exp(1j * phase)
                
            field += component_field
        return 20 * np.log10(np.abs(field))


