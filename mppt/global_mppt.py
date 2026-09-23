from typing import Callable, Any
from .base import MPPTBase, MPPTState
from .perturb_observe import PerturbAndObserve

class ScanningGlobalMPPT(MPPTBase):
    """
    Global MPPT Algorithm utilizing a wide range Duty Cycle scan.
    
    Useful for partial shading conditions where multiple local maxima exist 
    on the P-V curve. After identifying the global peak via sweeping, 
    a P&O algorithm is used for fine local tracking.
    """
    def __init__(self, D_init: float = 0.5, D_step: float = 0.005, 
                 D_min: float = 0.05, D_max: float = 0.90, scan_step: float = 0.01):
        super().__init__(D_init, D_step, D_min, D_max)
        self.scan_step = scan_step
        self.fine_tracker = PerturbAndObserve(D_init, D_step, D_min, D_max)
        self.global_found = False

    def scan_and_find_global(self, pv_module_or_array: Any, converter: Any, solver: Callable[[Any, Any, float], tuple[float, float]] = None) -> float:
        """
        Sweeps the duty cycle from D_min to D_max, recording V, I, P at each step
        to find the global maximum power point.
        
        Args:
            pv_module_or_array: The PV system model.
            converter: The power converter model.
            solver: A callable that takes (pv, converter, D) and returns (V, I).
                    If None, it expects a `.get_operating_point(converter, D)` method on PV.
                    
        Returns:
            The duty cycle D that yields the global maximum power.
        """
        import numpy as np
        
        best_P = -1.0
        best_D = self.D_min
        best_state = None
        
        D_sweep = np.arange(self.D_min, self.D_max + self.scan_step, self.scan_step)
        
        for d_val in D_sweep:
            d_val = self._clamp_D(d_val)
            
            if solver:
                v_val, i_val = solver(pv_module_or_array, converter, d_val)
            else:
                # Fallback to duck-typing standard methods
                v_val, i_val = pv_module_or_array.get_operating_point(converter, d_val)
                
            p_val = v_val * i_val
            
            # Record state
            scan_state = MPPTState(V=v_val, I=i_val, P=p_val, D=d_val, direction=0)
            self.history.append(scan_state)
            
            if p_val > best_P:
                best_P = p_val
                best_D = d_val
                best_state = scan_state
                
        # Set to the best observed D
        self.D = best_D
        self.state = best_state
        self.global_found = True
        
        # Initialize fine tracker at the global peak
        self.fine_tracker.D = best_D
        self.fine_tracker.reset()
        
        return best_D

    def step(self, V: float, I: float, D_current: float) -> float:
        """
        Execute one step of the MPPT.
        If the global scan has not been performed yet, this will raise a runtime warning/error
        in typical contexts, but for simulation step logic, we use P&O if standard step is called.
        """
        if not self._initialized:
            self.state = MPPTState(V=V, I=I, P=V*I, D=D_current, direction=0)
            self._initialized = True
            
        if not self.global_found:
            # If step is called before scan_and_find_global, act as pass-through 
            # or you could trigger a dynamic scan here if you had access to the models.
            pass
            
        # Defer to fine tracker
        new_D = self.fine_tracker.step(V, I, D_current)
        
        # Sync states
        self.D = new_D
        self.state = self.fine_tracker.state
        self.history.append(self.state)
        return new_D

    def reset(self):
        """Reset both global scanning state and fine tracker."""
        super().reset()
        self.global_found = False
        self.fine_tracker.reset()
