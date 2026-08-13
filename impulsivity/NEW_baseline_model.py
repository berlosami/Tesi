from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from NEW_agent import ForagerAgent

class BaselineModel(Model):
    N_AGENTS = 100
    T = 110
    INITIAL_AGE = 10
    INITIAL_ENERGY = 0.0
    R1 = 2.0
    R2 = 20.0
    D2 = 7
    METABOLIC_COST = 0.0
    mortality_scale = 0.0
    GRID_WIDTH = 20
    GRID_HEIGHT = 20
    LAMBDA_MIN = 0.05
    LAMBDA_MAX = 0.50

    def __init__(self, seed=None):
        super().__init__(seed=seed)
        self.grid = MultiGrid(self.GRID_WIDTH, self.GRID_HEIGHT, torus=True)
        self.agents_list = []

        for i in range(self.N_AGENTS):
            lam = self.random.uniform(self.LAMBDA_MIN, self.LAMBDA_MAX)
            agent = ForagerAgent(i, self, lam, self.INITIAL_ENERGY)
            self.agents_list.append(agent)
            self.grid.place_agent(
                agent,
                (self.random.randrange(self.GRID_WIDTH),
                 self.random.randrange(self.GRID_HEIGHT))
            )

        self.datacollector = DataCollector(model_reporters={
            "Population": self.get_population,
            "Mean Energy": self.get_mean_energy,
            "Mean Energy Patient": self.get_mean_energy_patient,
            "Mean Energy Impulsive": self.get_mean_energy_impulsive,
            "Mean Lambda x100": self.get_mean_lambda,
            "Lambda Variance x1000": self.get_lambda_variance,
            "Patient Fraction": self.get_patient_fraction,
            "Impulsive Fraction": self.get_impulsive_fraction,
            "Deaths Patient": self.get_deaths_patient,
            "Deaths Impulsive": self.get_deaths_impulsive,
        })
        self.running = True

    def get_mortality_probability(self, age):
        return 0.0

    def get_alive_agents(self):
        return [a for a in self.agents_list if a.alive]

    def get_population(self):
        return len(self.get_alive_agents())

    def get_mean_energy(self):
        alive = self.get_alive_agents()
        return float("nan") if not alive else sum(a.energy for a in alive) / len(alive)

    def get_mean_energy_patient(self):
        a = [x for x in self.get_alive_agents() if x.get_strategy() == "patient"]
        return float("nan") if not a else sum(x.energy for x in a) / len(a)

    def get_mean_energy_impulsive(self):
        a = [x for x in self.get_alive_agents() if x.get_strategy() == "impulsive"]
        return float("nan") if not a else sum(x.energy for x in a) / len(a)

    def get_mean_lambda(self):
        alive = self.get_alive_agents()
        if not alive:
            return float("nan")
        return 100.0 * sum(a.lambda_value for a in alive) / len(alive)

    def get_lambda_variance(self):
        alive = self.get_alive_agents()
        if len(alive) < 2:
            return float("nan")
        m = sum(a.lambda_value for a in alive) / len(alive)
        v = sum((a.lambda_value - m) ** 2 for a in alive) / len(alive)
        return 1000.0 * v

    def get_patient_fraction(self):
        alive = self.get_alive_agents()
        if not alive:
            return float("nan")
        return sum(a.get_strategy() == "patient" for a in alive) / len(alive)

    def get_impulsive_fraction(self):
        alive = self.get_alive_agents()
        if not alive:
            return float("nan")
        return sum(a.get_strategy() == "impulsive" for a in alive) / len(alive)

    def get_deaths_patient(self):
        return sum((not a.alive) and a.get_strategy() == "patient" for a in self.agents_list)

    def get_deaths_impulsive(self):
        return sum((not a.alive) and a.get_strategy() == "impulsive" for a in self.agents_list)

    def step(self):
        agents = list(self.agents_list)
        self.random.shuffle(agents)
        for agent in agents:
            agent.step()
        self.datacollector.collect(self)
