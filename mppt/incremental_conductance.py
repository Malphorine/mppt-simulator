from .base import MPPTBase, MPPTState

class IncrementalConductance(MPPTBase):
    """
    Incremental Conductance (INC) MPPT Algorithm.
    
    Based on the condition dP/dV = 0 at the MPP, which implies I + V*(dI/dV) = 0.
    For a boost converter:
    - Left of MPP (V < Vmp): dI/dV > -I/V -> Decrease D to increase V toward Vmp
    - Right of MPP (V > Vmp): dI/dV < -I/V -> Increase D to decrease V toward Vmp
    """
    def __init__(self, D_init: float = 0.5, D_step: float = 0.005, D_min: float = 0.05, D_max: float = 0.90, epsilon: float = 1e-4):
        super().__init__(D_init, D_step, D_min, D_max)
        self.epsilon = epsilon
        self.V_prev = 0.0
        self.I_prev = 0.0

    def step(self, V: float, I: float, D_current: float) -> float:
        """
        Execute one Incremental Conductance MPPT step.
        """
        P = V * I

        if not self._initialized:
            self.V_prev = V
            self.I_prev = I
            self.state = MPPTState(V=V, I=I, P=P, D=D_current, direction=0)
            self._initialized = True
            
            # Initial arbitrary perturbation
            new_D = self._clamp_D(D_current + self.D_step)
            self.state.D = new_D
            self.history.append(MPPTState(**self.state.__dict__))
            return new_D

        dV = V - self.V_prev
        dI = I - self.I_prev
        direction = 0  # 0 means hold, +1 means increase D, -1 means decrease D

        if abs(dV) < self.epsilon:
            if abs(dI) < self.epsilon:
                # At MPP
                direction = 0
            elif dI > 0:
                # Left of MPP, need to increase V -> Decrease D
                direction = -1
            else:
                # Right of MPP, need to decrease V -> Increase D
                direction = 1
        else:
            di_dv = dI / dV
            neg_i_v = -I / V
            
            if abs(di_dv - neg_i_v) < self.epsilon:
                # At MPP
                direction = 0
            elif di_dv > neg_i_v:
                # Left of MPP (V < Vmp) -> Decrease D to increase V
                direction = -1
            else:
                # Right of MPP (V > Vmp) -> Increase D to decrease V
                direction = 1

        if direction == 1:
            new_D = self._clamp_D(D_current + self.D_step)
        elif direction == -1:
            new_D = self._clamp_D(D_current - self.D_step)
        else:
            new_D = D_current

        # Update state and history
        self.state = MPPTState(V=V, I=I, P=P, D=new_D, direction=direction if direction != 0 else self.state.direction)
        self.history.append(MPPTState(**self.state.__dict__))

        self.V_prev = V
        self.I_prev = I
        self.D = new_D
        return new_D
