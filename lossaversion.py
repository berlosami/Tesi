import random
import numpy as np
import pandas as pd
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

# =========================
# AGENTE
# =========================
class StressAgent(Agent):
    def __init__(self, unique_id, model, lambda_level):
        super().__init__(unique_id)
        self.model = model
        self.lambda_ = lambda_level  # livello di loss aversion
        self.lambda_base = lambda_level
        self.wealth = 1.0
        self.alive = True

    def step(self):
        if not self.alive:
            return

        # --- Stress acuto (10% di probabilità) ---
        if random.random() < 0.1:
            self.lambda_ = self.lambda_base * random.uniform(1.5, 2.0)
        else:
            self.lambda_ = self.lambda_base

        # --- Ambiente e condizioni ---
        env = self.model.env_params
        safe_reward = env["safe_reward"]
        p_loss = env["p_loss"]
        p_gain = 1 - p_loss

        # --- Gamble outcomes ---
        gain = 0.2
        loss = -0.1

        # --- Subjective value (solo loss aversion) ---
        sv_gamble = p_gain * gain + p_loss * (-self.lambda_ * abs(loss))
        sv_safe = safe_reward

        # --- Scelta probabilistica in base alla differenza di SV ---
        prob_gamble = 1 / (1 + np.exp(-(sv_gamble - sv_safe) * 10))
        if random.random() < prob_gamble:
            # Esito reale del gamble
            outcome = gain if random.random() < p_gain else loss
        else:
            outcome = safe_reward

        # --- Aggiornamento ricchezza ---
        self.wealth += outcome

        # --- Condizione di "morte" economica ---
        if self.wealth <= 0:
            self.alive = False

# =========================
# MODELLO
# =========================
class StressModel(Model):
    def __init__(self, N, lambda_level, env_params, steps=50):
        super().__init__()
        self.num_agents = N
        self.env_params = env_params
        self.steps = steps

        # Griglia spaziale semplice (solo per completezza)
        self.grid = MultiGrid(10, 10, True)

        # Creazione agenti
        self.agents = []
        for i in range(self.num_agents):
            a = StressAgent(i, self, lambda_level)
            self.agents.append(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # Raccolta dati
        self.datacollector = DataCollector(
            model_reporters={
                "AvgWealth": lambda m: np.mean([a.wealth for a in m.agents if a.alive]),
                "Alive": lambda m: sum([a.alive for a in m.agents])
            }
        )

    def step(self):
        for agent in self.agents:
            agent.step()
        self.datacollector.collect(self)

# =========================
# FUNZIONE DI SIMULAZIONE
# =========================
def run_simulation(lambda_level, env_params, label):
    model = StressModel(N=50, lambda_level=lambda_level, env_params=env_params)
    for i in range(model.steps):
        model.step()
    df = model.datacollector.get_model_vars_dataframe()
    df["Condition"] = label
    return df

# =========================
# PARAMETRI DELLE 4 CONDIZIONI
# =========================
lambda_high = 2.0
lambda_low = 1.2

env_stable = {"p_loss": 0.1, "safe_reward": 0.05}
env_unstable = {"p_loss": 0.4, "safe_reward": 0.02}

# =========================
# ESECUZIONE DELLE 4 CONDIZIONI
# =========================
results_high_stable = run_simulation(lambda_high, env_stable, "High λ - Stable")
results_high_unstable = run_simulation(lambda_high, env_unstable, "High λ - Unstable")
results_low_stable = run_simulation(lambda_low, env_stable, "Low λ - Stable")
results_low_unstable = run_simulation(lambda_low, env_unstable, "Low λ - Unstable")

# =========================
# UNIONE RISULTATI
# =========================
results = pd.concat([
    results_high_stable,
    results_high_unstable,
    results_low_stable,
    results_low_unstable
])

# =========================
# OUTPUT
# =========================
print(results.groupby("Condition")[["AvgWealth", "Alive"]].tail(1))
