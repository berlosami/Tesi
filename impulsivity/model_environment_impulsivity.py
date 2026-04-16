from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np

from agent_environment_impulsivity import SurvivalAgent
from environment_impulsivity import (
    StableEnvironment,
    VolatileEnvironment,
    HarshEnvironment
)

PARAMS = {
    "T": 60,
    "N0": 100,

    "E0": 10.0,
    "E_MAX": 30.0,

    "METABOLIC_COST": 2.0,

    "R1": 2.0,
    "D1": 1.0,

    "R2": 4.0,
    "D2": 4.0,

    "SEED": 123,

    "WIDTH": 20,
    "HEIGHT": 20,

    "ENVIRONMENT": "stable",

    # probabilità successo reward futura
    "P_R2_SUCCESS": 0.5,
}


class SurvivalModel(Model):
    def __init__(self, p=PARAMS):
        super().__init__()

        self.p = p.copy()

        self.schedule = RandomActivation(self)

        self.grid = MultiGrid(
            self.p["WIDTH"],
            self.p["HEIGHT"],
            torus=True
        )

        self.environment = self.make_environment()

        self.init_population()

        self.datacollector = DataCollector(

        model_reporters={

            "Population": lambda m:
                sum(a.alive for a in m.schedule.agents),

            "MeanLambdaAlive": lambda m: (
                np.mean([a.lam for a in m.schedule.agents if a.alive]) * 100
                if any(a.alive for a in m.schedule.agents)
                else 0
            ),

            "MeanEnergyAlive": lambda m: (
                np.mean([a.E for a in m.schedule.agents if a.alive])
                if any(a.alive for a in m.schedule.agents)
                else 0
            ),

            "VarLambdaAlive": lambda m: (
                np.var([a.lam for a in m.schedule.agents if a.alive]) * 1000
                if any(a.alive for a in m.schedule.agents)
                else 0
            ),
        },

        agent_reporters={

            "Lambda": "lam",
            "Energy": "E",
            "Alive": "alive"
        }
    )

    def make_environment(self):
        env = self.p["ENVIRONMENT"]

        if env == "stable":
            return StableEnvironment(self)

        elif env == "volatile":
            return VolatileEnvironment(self)

        elif env == "harsh":
            self.p["METABOLIC_COST"] = 3.0
            return HarshEnvironment(self)

        else:
            return StableEnvironment(self)

    def init_population(self):
        rng = np.random.default_rng(self.p["SEED"])

        # lambda continuo invece di 2 gruppi fissi
        lambdas = rng.uniform(
            0.05,
            0.50,
            self.p["N0"]
        )

        for i in range(self.p["N0"]):
            # energia iniziale leggermente variabile
            E_init = rng.uniform(8.0, 12.0)

            a = SurvivalAgent(
                i,
                self,
                float(lambdas[i]),
                E_init
            )

            self.schedule.add(a)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)

            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)