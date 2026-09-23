from .base import MPPTBase, MPPTState

class PerturbAndObserve(MPPTBase):
    """
    Perturb & Observe (P&O) MPPT Algorithm.
    
    This implementation accounts for the physics of a boost converter:
    - Increasing Duty Cycle (D) decreases the effective input resistance.
    - Decreasing input resistance decreases the PV operating voltage.
    """
    def __init__(self, D_init: float = 0.5, D_step: float = 0.005, D_min: float = 0.05, D_max: float = 0.90, p_tol: float = 1e-4):
        super().__init__(D_init, D_step, D_min, D_max)
        self.p_tol = p_tol
        self.P_prev = 0.0

    def step(self, V: float, I: float, D_current: float) -> float:
        """
        Execute one P&O MPPT step.
        """
        P = V * I

        if not self._initialized:
            # First step initialization
            self.P_prev = P
            self.state = MPPTState(V=V, I=I, P=P, D=D_current, direction=1)
            self._initialized = True
            
            # Start by perturbing in the positive direction
            new_D = self._clamp_D(D_current + self.D_step)
            self.state.D = new_D
            self.history.append(MPPTState(**self.state.__dict__))
            return new_D

        dP = P - self.P_prev
        direction = self.state.direction

        if abs(dP) < self.p_tol:
            # Power hasn't changed significantly; hold current duty cycle
            direction = 0
        elif dP > 0:
            # Power increased, keep moving in the same direction
            pass 
        else:
            # Power decreased, reverse the perturbation direction
            direction = -direction

        # Calculate new duty cycle
        if direction != 0:
            new_D = self._clamp_D(D_current + direction * self.D_step)
        else:
            new_D = D_current

        # Update state and history
        self.state = MPPTState(V=V, I=I, P=P, D=new_D, direction=direction if direction != 0 else self.state.direction)
        self.history.append(MPPTState(**self.state.__dict__))
        
        self.P_prev = P
        self.D = new_D
        return new_D
