from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agent_baseline_impulsivity import SurvivalAgent

import numpy as np


PARAMS = {
    "T": 60,
    "N0": 100,
    "E0": 10.0,
    "E_MAX": 30.0,
    "METABOLIC_COST": 2.0,
    "R1": 2.0, "D1": 1.0,
    "R2": 4.0, "D2": 4.0,
    "R1_SUPPLY_PER_DAY": 10000,
    "R2_SUPPLY_PER_DAY": 10000,
    "LAMBDA_LOW": 0.1,
    "LAMBDA_HIGH": 0.4,
    "FRAC_LOW": 0.5,
    "SEED": 123
}


class SurvivalModel(Model):
    def __init__(self, p):
        super().__init__()
        self.p = p
        self.schedule = RandomActivation(self)

        self.r1_supply = 0
        self.r2_supply = 0

        # inizializzazione popolazione
        self.init_population()

        self.datacollector = DataCollector(
            model_reporters={
                "Population": lambda m: sum(a.alive for a in m.schedule.agents)
            }
        )

    def init_population(self):
        rng = np.random.default_rng(self.p["SEED"])

        n_low = int(self.p["FRAC_LOW"] * self.p["N0"])
        lambdas = ([self.p["LAMBDA_LOW"]] * n_low +
                   [self.p["LAMBDA_HIGH"]] * (self.p["N0"] - n_low))

        rng.shuffle(lambdas)

        for i in range(self.p["N0"]):
            a = SurvivalAgent(i, self, lambdas[i], self.p["E0"])
            self.schedule.add(a)

    def reset_day(self):
        self.r1_supply = self.p["R1_SUPPLY_PER_DAY"]
        self.r2_supply = self.p["R2_SUPPLY_PER_DAY"]

    def step(self):
        self.reset_day()
        self.schedule.step()
        self.datacollector.collect(self)


if __name__ == "__main__":
    model = SurvivalModel(PARAMS)

    for i in range(PARAMS["T"]):
        model.step()

    df = model.datacollector.get_model_vars_dataframe()
    print(df.tail())

    print("Simulazione completata")