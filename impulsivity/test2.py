from mesa import Agent, Model
from mesa.space import MultiGrid
import random

class ForagerAgent(Agent):
    def __init__(self, model, sex):
        super().__init__(model)
        self.sex = sex
        self.age = 0
        self.energy = self.init_energy()
        self.alive = True

    def init_energy(self):
        return random.uniform(40, 60) if self.sex == "M" else random.uniform(50, 70)

    def metabolic_cost(self):
        return 1.2 if self.sex == "M" else 1.0

    def choose_option(self):
        if self.energy < 30:
            return "risky"
        return random.choice(["safe", "risky"])

    def safe_option(self):
        self.energy += self.model.safe_gain

    def risky_option(self):
        if random.random() < self.model.risky_success_prob:
            self.energy += self.model.risky_gain
        else:
            self.energy -= self.model.risky_loss

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_pos = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_pos)
        self.energy -= self.model.movement_cost

    def step(self):
        if not self.alive:
            return

        self.age += 1
        self.energy -= self.metabolic_cost()

        choice = self.choose_option()
        if choice == "safe":
            self.safe_option()
        else:
            self.risky_option()

        self.move()

        if self.energy <= 0:
            self.alive = False
            self.remove()

class ForagingModel(Model):
    def __init__(self, N=50, width=10, height=10, environment_type="stable"):
        super().__init__()

        self.environment_type = environment_type
        self.grid = MultiGrid(width, height, torus=True)

        if environment_type == "stable":
            self.safe_gain = 4
            self.risky_gain = 8
            self.risky_loss = 4
            self.risky_success_prob = 0.6
        else:
            self.safe_gain = 2
            self.risky_gain = 12
            self.risky_loss = 6
            self.risky_success_prob = 0.4

        self.movement_cost = 0.5
        self.day = 0

        for _ in range(N):
            sex = random.choice(["M", "F"])
            agent = ForagerAgent(self, sex)
            self.grid.place_agent(
                agent,
                (random.randrange(width), random.randrange(height))
            )

    def step(self):
        self.day += 1
        for agent in list(self.agents):
            agent.step()

model = ForagingModel(environment_type="unstable")

for day in range(365):
    model.step()

print("Agenti vivi unstable:", len(model.agents))

model2 = ForagingModel(environment_type="stable")

for day in range(365):
    model2.step()

print("Agenti vivi stable:", len(model2.agents))
