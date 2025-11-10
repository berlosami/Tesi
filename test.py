import random
import numpy as np
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

# ---- SCHEDULER CUSTOM ----
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

# ---- AGENTE ----
class StressAgent(Agent):
    """Agente con loss aversion (λ) e stress."""
    def __init__(self, model):
        super().__init__(model)
        self.lambda_ = random.uniform(1.5, 2.5)
        self.lambda_base = self.lambda_
        self.wealth = 1.0
        self.stress = 0

    def step(self):
        # Stress acuto
        if random.random() < 0.1:
            self.lambda_ = self.lambda_base * 1.5
            self.stress = 1
        else:
            self.lambda_ = self.lambda_base
            self.stress = 0

        # Decisione gamble vs safe
        gamble_outcomes = [0.2, -0.1]
        safe_reward = 0.05

        sv_gamble = np.mean([x if x >= 0 else -self.lambda_ * abs(x) for x in gamble_outcomes])
        sv_safe = safe_reward

        if sv_gamble > sv_safe:
            outcome = random.choice(gamble_outcomes)
        else:
            outcome = safe_reward

        self.wealth += outcome

        # Rimozione sicura se l’agente è "morto"
        if self.wealth <= 0:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            return

        # Movimento casuale
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

# ---- MODELLO ----
class StressModel(Model):
    """Modello con griglia, scheduler custom e raccolta dati."""
    def __init__(self, N=50, width=10, height=10):
        super().__init__()
        self.num_agents = N
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.running = True

        for _ in range(self.num_agents):
            a = StressAgent(self)
            self.schedule.add(a)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            model_reporters={"AvgWealth": lambda m: np.mean([a.wealth for a in m.schedule.agents])}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if len(self.schedule.agents) == 0:
            self.running = False

# ---- ESEMPIO DI ESECUZIONE ----
if __name__ == "__main__":
    model = StressModel(N=10, width=5, height=5)
    steps = 20
    for i in range(steps):
        if model.running:
            model.step()
            print(f"Step {i+1}: Wealths = {[a.wealth for a in model.schedule.agents]}")
        else:
            print("Tutti gli agenti sono morti.")
            break

    # Dati medi raccolti
    print("Media Wealth raccolta:")
    print(model.datacollector.get_model_vars_dataframe())







