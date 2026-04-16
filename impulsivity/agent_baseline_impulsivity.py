from mesa import Agent
import numpy as np

class SurvivalAgent(Agent):
    def __init__(self, unique_id, model, lam, E):
        super().__init__(unique_id, model)
        self.lam = lam
        self.E = E
        self.alive = True

    def subjective_value(self, R, D):
        return R * np.exp(-self.lam * D)

    def choose(self):
        p = self.model.p
        sv1 = self.subjective_value(p["R1"], p["D1"])
        sv2 = self.subjective_value(p["R2"], p["D2"])
        return 1 if sv1 > sv2 else 2

    def step(self):
        if not self.alive:
            return

        p = self.model.p

        # costo metabolico
        self.E -= p["METABOLIC_COST"]
        if self.E <= 0:
            self.alive = False
            return

        choice = self.choose()

        if choice == 1:
            if self.model.r1_supply > 0:
                self.model.r1_supply -= 1
                reward = p["R1"]
            else:
                reward = 0
        else:
            if self.model.r2_supply > 0:
                self.model.r2_supply -= 1
                reward = p["R2"]
            else:
                reward = 0

        self.E = min(self.E + reward, p["E_MAX"])
