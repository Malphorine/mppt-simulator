"""
Load Models for MPPT Simulator.

This module provides different types of electrical loads that can be connected
to the output of the DC-DC converter.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

class LoadBase(ABC):
    """Abstract base class for all load models."""
    
    @abstractmethod
    def get_current(self, V: float) -> float:
        """
        Calculate the current drawn by the load at a given voltage.
        
        Args:
            V: Voltage applied to the load [V]
            
        Returns:
            Current drawn by the load [A]
        """
        pass

@dataclass
class ResistiveLoad(LoadBase):
    """
    A simple resistive load.
    
    Attributes:
        R (float): Resistance in Ohms. Default is 20.0 Ω.
    """
    R: float = 20.0
    
    def get_current(self, V: float) -> float:
        """I = V / R"""
        if self.R <= 0:
            raise ValueError("Resistance must be greater than zero.")
        return V / self.R

@dataclass
class ConstantPowerLoad(LoadBase):
    """
    A constant power load.
    
    Attributes:
        P_target (float): Target power in Watts.
        V_min (float): Minimum voltage below which the load draws maximum clamped current
                       to avoid division by zero or infinite current.
    """
    P_target: float = 100.0
    V_min: float = 1.0
    
    def get_current(self, V: float) -> float:
        """I = P_target / V, clamped to avoid infinite current at 0V."""
        V_clamped = max(V, self.V_min)
        return self.P_target / V_clamped

@dataclass
class BatteryLoad(LoadBase):
    """
    A battery load modeled as an ideal voltage source with series internal resistance.
    
    Attributes:
        V_battery (float): Nominal battery voltage in Volts.
        R_internal (float): Internal resistance of the battery in Ohms.
    """
    V_battery: float = 48.0
    R_internal: float = 0.1
    
    def get_current(self, V: float) -> float:
        """
        I = (V - V_battery) / R_internal
        Only draws current when V > V_battery (charging), otherwise returns 0 
        or negative current (discharging) depending on the system configuration.
        Assuming here the converter only pushes current to the battery.
        """
        if self.R_internal <= 0:
            raise ValueError("Internal resistance must be greater than zero.")
            
        I = (V - self.V_battery) / self.R_internal
        # Usually, a unidirectional DC-DC converter cannot pull current from the load,
        # so we clamp the current to >= 0.
        return max(0.0, I)
