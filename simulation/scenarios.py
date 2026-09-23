"""
Environmental scenarios for MPPT simulation.
Defines time-varying irradiance and temperature profiles.
"""

from dataclasses import dataclass
from typing import Tuple, List, Dict
import numpy as np

@dataclass
class ScenarioConfig:
    name: str
    description: str
    duration: float  # seconds

class Scenario:
    """Base class for all environmental scenarios."""
    
    def __init__(self, config: ScenarioConfig):
        self.config = config
    
    def get_conditions(self, t: float) -> Tuple[float, float]:
        """
        Return environmental conditions at time t.
        
        Args:
            t (float): Time in seconds
            
        Returns:
            Tuple[float, float]: (irradiance [W/m²], temperature [°C])
        """
        raise NotImplementedError
    
    def get_change_times(self) -> List[float]:
        """
        Return times at which environmental conditions change.
        Used for graph annotations.
        
        Returns:
            List[float]: List of change times in seconds
        """
        return []
    
    @property
    def name(self) -> str:
        return self.config.name

class ConstantConditions(Scenario):
    """Scenario with constant irradiance and temperature."""
    
    def __init__(self, name: str, description: str, G: float, T: float, duration: float):
        super().__init__(ScenarioConfig(name=name, description=description, duration=duration))
        self.G = float(G)
        self.T = float(T)
        
    def get_conditions(self, t: float) -> Tuple[float, float]:
        return self.G, self.T

class IrradianceStep(Scenario):
    """Scenario with a step change in irradiance at a specific time."""
    
    def __init__(self, name: str, description: str, G_start: float, G_end: float, T: float, t_change: float, duration: float):
        super().__init__(ScenarioConfig(name=name, description=description, duration=duration))
        self.G_start = float(G_start)
        self.G_end = float(G_end)
        self.T = float(T)
        self.t_change = float(t_change)
        
    def get_conditions(self, t: float) -> Tuple[float, float]:
        G = self.G_start if t < self.t_change else self.G_end
        return G, self.T
        
    def get_change_times(self) -> List[float]:
        return [self.t_change]

class TemperatureRamp(Scenario):
    """Scenario with a step/ramp change in temperature at a specific time."""
    
    def __init__(self, name: str, description: str, G: float, T_start: float, T_end: float, t_change: float, duration: float):
        super().__init__(ScenarioConfig(name=name, description=description, duration=duration))
        self.G = float(G)
        self.T_start = float(T_start)
        self.T_end = float(T_end)
        self.t_change = float(t_change)
        
    def get_conditions(self, t: float) -> Tuple[float, float]:
        # Implementing as a step change as per specification
        T = self.T_start if t < self.t_change else self.T_end
        return self.G, T
        
    def get_change_times(self) -> List[float]:
        return [self.t_change]

class CombinedVariation(Scenario):
    """Scenario with multiple step changes in both irradiance and temperature."""
    
    def __init__(self, name: str, description: str, duration: float):
        super().__init__(ScenarioConfig(name=name, description=description, duration=duration))
        
    def get_conditions(self, t: float) -> Tuple[float, float]:
        """Example logic: G=1000 for first 10s then G=700, T=25 for first 15s then T=40"""
        G = 1000.0 if t < 10.0 else 700.0
        T = 25.0 if t < 15.0 else 40.0
        return G, T
        
    def get_change_times(self) -> List[float]:
        return [10.0, 15.0]

class PartialShading(Scenario):
    """
    Scenario for partial shading across multiple PV modules.
    Provides individual irradiances and temperatures for each module.
    """
    
    def __init__(self, name: str, description: str, duration: float, G_modules: List[float], T_modules: List[float]):
        super().__init__(ScenarioConfig(name=name, description=description, duration=duration))
        self.G_modules = [float(g) for g in G_modules]
        self.T_modules = [float(t) for t in T_modules]
        
    def get_conditions(self, t: float) -> Tuple[float, float]:
        """Fallback for single-condition queries: returns average conditions."""
        avg_G = sum(self.G_modules) / len(self.G_modules) if self.G_modules else 0.0
        avg_T = sum(self.T_modules) / len(self.T_modules) if self.T_modules else 0.0
        return avg_G, avg_T
        
    def get_module_conditions(self, t: float) -> Tuple[List[float], List[float]]:
        """
        Return environmental conditions for each module.
        
        Args:
            t (float): Time in seconds
            
        Returns:
            Tuple[List[float], List[float]]: (List of irradiances [W/m²], List of temperatures [°C])
        """
        return self.G_modules, self.T_modules

def get_all_scenarios() -> Dict[str, Scenario]:
    """
    Returns a dictionary of standard pre-defined scenarios.
    
    Returns:
        Dict[str, Scenario]: Dictionary mapping scenario names to Scenario objects.
    """
    return {
        'constant_stc': ConstantConditions(
            name='STC', 
            description='Standard Test Conditions: Constant 1000 W/m², 25°C', 
            G=1000.0, T=25.0, duration=20.0
        ),
        'constant_low_irr': ConstantConditions(
            name='Low Irradiance', 
            description='Constant 700 W/m², 25°C', 
            G=700.0, T=25.0, duration=20.0
        ),
        'constant_hot': ConstantConditions(
            name='Hot Conditions', 
            description='Constant 500 W/m², 40°C', 
            G=500.0, T=40.0, duration=20.0
        ),
        'irradiance_drop': IrradianceStep(
            name='Irradiance Drop', 
            description='Irradiance step decrease: 1000 -> 600 W/m² at t=10s', 
            G_start=1000.0, G_end=600.0, T=25.0, t_change=10.0, duration=20.0
        ),
        'irradiance_rise': IrradianceStep(
            name='Irradiance Rise', 
            description='Irradiance step increase: 600 -> 1000 W/m² at t=10s', 
            G_start=600.0, G_end=1000.0, T=25.0, t_change=10.0, duration=20.0
        ),
        'temperature_rise': TemperatureRamp(
            name='Temperature Rise', 
            description='Temperature step increase: 25 -> 45°C at t=10s', 
            G=1000.0, T_start=25.0, T_end=45.0, t_change=10.0, duration=20.0
        ),
        'combined': CombinedVariation(
            name='Combined Variation', 
            description='Irradiance drops at t=10s, Temperature rises at t=15s', 
            duration=30.0
        )
    }
