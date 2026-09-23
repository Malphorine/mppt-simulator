import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class MPPTState:
    """State recorded at each MPPT step."""
    V: float = 0.0
    I: float = 0.0
    P: float = 0.0
    D: float = 0.5
    direction: int = 1  # +1 or -1

class MPPTBase(ABC):
    """
    Abstract base class for all Maximum Power Point Tracking (MPPT) algorithms.
    """
    def __init__(self, D_init: float = 0.5, D_step: float = 0.005, D_min: float = 0.05, D_max: float = 0.90):
        self.D = D_init
        self.D_step = D_step
        self.D_min = D_min
        self.D_max = D_max
        self.state = MPPTState(D=D_init)
        self.history: list[MPPTState] = []
        self._initialized = False
    
    @abstractmethod
    def step(self, V: float, I: float, D_current: float) -> float:
        """
        Execute one MPPT step based on the current PV voltage and current.
        
        Args:
            V: Current PV voltage in Volts.
            I: Current PV current in Amperes.
            D_current: The current duty cycle of the converter.
            
        Returns:
            The new computed duty cycle.
        """
        ...
    
    def _clamp_D(self, D: float) -> float:
        """
        Clamp the duty cycle within the allowable range [D_min, D_max].
        """
        return max(self.D_min, min(self.D_max, D))
    
    def reset(self):
        """
        Reset the MPPT tracker to its initial state.
        """
        self.D = self.state.D
        self._initialized = False
        self.history.clear()
    
    @property
    def name(self) -> str:
        return self.__class__.__name__
