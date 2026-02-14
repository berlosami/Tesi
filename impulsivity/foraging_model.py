from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import random

MAX_ENERGY = 20


class ForagerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy = 10
        self.last_choice = None

    def step(self):
        self.move()
        self.choose_option()
        self.energy -= 1  # costo metabolico

        if self.energy <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def choose_option(self):
        # Probabilità di scegliere il rischio (impulsività comportamentale)
        risky_choice_prob = 0.5

        # Ambiente = probabilità di successo del rischio
        if self.model.environment == "stable":
            success_prob = 0.7
        else:  # unstable
            success_prob = 0.3

        if self.random.random() < risky_choice_prob:
            self.last_choice = "risky"
            if self.random.random() < success_prob:
                self.energy += 4
            else:
                self.energy += 0
        else:
            self.last_choice = "safe"
            self.energy += 2

        # saturazione biologica dell’energia
        self.energy = min(self.energy, MAX_ENERGY)


class ForagingModel(Model):
    def __init__(self, n_agents=25, width=20, height=20, environment="stable"):
        super().__init__()
        self.environment = environment
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)

        for i in range(n_agents):
            agent = ForagerAgent(i, self)
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()

