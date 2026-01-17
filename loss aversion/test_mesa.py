

import mesa




from mesa import Agent, Model
from mesa.space import MultiGrid

from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization import ModularServer

import random
import numpy as np
import random

class RandomActivation:
    """Scheduler minimale che attiva casualmente tutti gli agenti."""
    def __init__(self, model):
        self.model = model
        self.agents = []

    def add(self, agent):
        self.agents.append(agent)

    def remove(self, agent):
        if agent in self.agents:
            self.agents.remove(agent)

    def step(self):
        for agent in random.sample(self.agents, len(self.agents)):
            agent.step()

class StressAgent(Agent):
    """Agente con solo loss aversion (λ) e stress."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.lambda_ = random.uniform(1.5, 2.5)  # avversione alle perdite
        self.lambda_base = self.lambda_
        self.wealth = 1.0
        self.stress = 0.0

    def step(self):
        # Stress acuto (aumenta lambda temporaneamente)
        if random.random() < 0.1:
            self.lambda_ = self.lambda_base * 1.5
            self.stress = 1
        else:
            self.lambda_ = self.lambda_base
            self.stress = 0

        # Scelta semplice: gamble vs safe
        gamble_outcomes = [0.2, -0.1]
        safe_reward = 0.05

        sv_gamble = np.mean([x if x >= 0 else -self.lambda_ * abs(x) for x in gamble_outcomes])
        sv_safe = safe_reward

        if sv_gamble > sv_safe:
            outcome = random.choice(gamble_outcomes)
        else:
            outcome = safe_reward

        self.wealth += outcome
        if self.wealth <= 0:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

        # Movimento casuale
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)


class StressModel(Model):
    """Modello con griglia e visualizzazione tipo NetLogo."""
    def __init__(self, N=100, width=10, height=10):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        for i in range(self.num_agents):
            a = StressAgent(i, self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            model_reporters={"AvgWealth": lambda m: np.mean([a.wealth for a in m.schedule.agents])}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if len(self.schedule.agents) == 0:
            self.running = False


# ---- VISUALIZZAZIONE ----

def agent_portrayal(agent):
    """Come visualizzare ogni agente nella griglia."""
    if agent is None:
        return

    color = "red" if agent.stress == 1 else "blue"
    size = 0.8 if agent.stress == 1 else 0.6

    portrayal = {
        "Shape": "circle",
        "Color": color,
        "Filled": "true",
        "r": size,
    }
    return portrayal


grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

chart = ChartModule(
    [{"Label": "AvgWealth", "Color": "green"}],
    data_collector_name="datacollector"
)

server = ModularServer(
    StressModel,
    [grid, chart],
    "Stress & Loss Aversion Model",
    {"N": 50, "width": 10, "height": 10}
)

server.port = 8521
server.launch()


