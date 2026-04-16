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
        sv1 = self.subjective_value(p['R1'], p['D1'])
        sv2 = self.subjective_value(p['R2'], p['D2'])
        return 1 if sv1 > sv2 else 2

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        if not self.alive:
            return

        self.move()
        p = self.model.p
        env = self.model.environment

        self.E -= p['METABOLIC_COST']
        if self.E <= 0:
            self.alive = False
            return

        choice = self.choose()
        reward = env.get_reward(choice)
        self.E = min(self.E + reward, p['E_MAX'])