from mesa import Agent
import math

class ForagerAgent(Agent):
    def __init__(self, unique_id, model, lambda_value, initial_energy):
        super().__init__(unique_id, model)
        self.lambda_value = float(lambda_value)
        self.energy = float(initial_energy)
        self.age = model.INITIAL_AGE
        self.alive = True
        self.pending_days = 0
        self.pending_reward = 0.0

    def get_strategy(self):
        threshold = math.log(self.model.R2 / self.model.R1) / self.model.D2
        return "patient" if self.lambda_value < threshold else "impulsive"

    def step(self):
        if not self.alive:
            return

        if self.pending_days > 0:
            self.pending_days -= 1
            if self.pending_days == 0:
                self.energy += self.pending_reward
                self.pending_reward = 0.0
        else:
            if self.get_strategy() == "impulsive":
                self.energy += self.model.R1
            else:
                self.pending_days = self.model.D2
                self.pending_reward = self.model.R2

        self.energy -= self.model.METABOLIC_COST

        if self.model.random.random() < self.model.get_mortality_probability(self.age):
            self.alive = False

        self.age += 1

        if self.alive and self.model.grid is not None:
            moves = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            if moves:
                self.model.grid.move_agent(self, self.random.choice(moves))

            def get_color(self):

             threshold = math.log(
             self.model.R2 / self.model.R1
    )        / self.model.D2

             if self.lambda_value < threshold - 0.05:
              return "green"

             elif self.lambda_value <= threshold + 0.05:
              return "yellow"

             else:
              return "red"