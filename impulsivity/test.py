from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random

# ------------------------
# AGENTE
# ------------------------

class ForagerAgent(Agent):
    def __init__(self, unique_id, model, sex):
        super().__init__(unique_id, model)
        self.sex = sex  # "M" o "F"
        self.age = 0  # in giorni
        self.energy = self.init_energy()
        self.alive = True

    def init_energy(self):
        if self.sex == "M":
            return random.uniform(40, 60)
        else:
            return random.uniform(50, 70)

    def metabolic_cost(self):
        return 1.2 if self.sex == "M" else 1.0

    def choose_option(self):
        """
        Scelta tra opzione sicura e rischiosa.
        Per ora molto semplice: dipende solo dall'energia
        (l'impulsività emergerà più avanti)
        """
        if self.energy < 30:
            return "risky"
        return random.choice(["safe", "risky"])

    def safe_option(self):
        gain = self.model.safe_gain
        self.energy += gain

    def risky_option(self):
        if random.random() < self.model.risky_success_prob:
            self.energy += self.model.risky_gain
        else:
            self.energy -= self.model.risky_loss

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)
        self.energy -= self.model.movement_cost

    def step(self):
        if not self.alive:
            return

        # invecchiamento
        self.age += 1

        # costo metabolico
        self.energy -= self.metabolic_cost()

        # decisione
        choice = self.choose_option()
        if choice == "safe":
            self.safe_option()
        else:
            self.risky_option()

        # movimento (sempre, per ora)
        self.move()

        # sopravvivenza
        if self.energy <= 0:
            self.alive = False
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)


# ------------------------
# MODELLO
# ------------------------

class ForagingModel(Model):
    def __init__(
        self,
        N=50,
        width=10,
        height=10,
        environment_type="stable"
    ):
        self.num_agents = N
        self.environment_type = environment_type

        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)

        # parametri ambiente
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

        # creazione agenti
        for i in range(self.num_agents):
            sex = random.choice(["M", "F"])
            agent = ForagerAgent(i, self, sex)
            self.schedule.add(agent)

            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        self.day = 0

    def step(self):
        self.day += 1
        self.schedule.step()
