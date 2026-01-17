# sweep_experiment.py
import os
import csv
import random
import numpy as np
import pandas as pd
from functools import partial
from itertools import product
from multiprocessing import Pool

# Importa i default; se hai salvato params_defaults.py nella stessa cartella, altrimenti definisci i valori qui:
try:
    from params_defaults import PARAMS_DEFAULTS as DEFAULTS
except Exception:
    DEFAULTS = {
        "lambda_typical": 2.0,
        "lambda_low": 1.2,
        "lambda_high": 3.0,
        "stress_prob": 0.10,
        "stress_multiplier": 1.5,
        "stress_duration": 1,
        "env_stable": {"p_loss": 0.10, "safe_reward": 0.05},
        "env_unstable": {"p_loss": 0.40, "safe_reward": 0.02},
        "gain": 0.20,
        "loss": -0.10,
        "N": 50,
        "steps": 50,
    }

# -----------------------
# Modello minimale (autonomo)
# -----------------------
class AgentMinimal:
    def __init__(self, unique_id, model, lambda_level):
        self.unique_id = unique_id
        self.model = model
        self.lambda_base = lambda_level
        self.lambda_ = lambda_level
        self.wealth = 1.0
        self.alive = True
        self.stress_time = 0

    def step(self):
        if not self.alive:
            return

        # stress event
        if random.random() < self.model.stress_prob:
            self.lambda_ = self.lambda_base * self.model.stress_multiplier
            self.stress_time = self.model.stress_duration
        elif self.stress_time > 0:
            self.stress_time -= 1
            if self.stress_time == 0:
                self.lambda_ = self.lambda_base

        # env params
        p_loss = self.model.env_params["p_loss"]
        p_gain = 1 - p_loss
        gain = self.model.gain
        loss = self.model.loss
        safe_reward = self.model.env_params["safe_reward"]

        # subjective value (loss aversion only)
        sv_gamble = p_gain * gain + p_loss * (-self.lambda_ * abs(loss))
        sv_safe = safe_reward

        # probabilistic choice based on SV difference
        prob_gamble = 1 / (1 + np.exp(-(sv_gamble - sv_safe) * 10))
        if random.random() < prob_gamble:
            outcome = gain if random.random() < p_gain else loss
        else:
            outcome = safe_reward

        self.wealth += outcome
        if self.wealth <= 0:
            self.alive = False

class ModelMinimal:
    def __init__(self, N, lambda_level, env_params, steps, gain, loss, stress_prob, stress_multiplier, stress_duration):
        self.N = N
        self.env_params = env_params
        self.steps = steps
        self.gain = gain
        self.loss = loss
        self.stress_prob = stress_prob
        self.stress_multiplier = stress_multiplier
        self.stress_duration = stress_duration
        self.agents = [AgentMinimal(i, self, lambda_level) for i in range(N)]

    def step(self):
        for a in self.agents:
            a.step()

    def run(self):
        records = []
        for t in range(self.steps):
            self.step()
            alive = sum(1 for a in self.agents if a.alive)
            avgw = np.mean([a.wealth for a in self.agents if a.alive]) if alive>0 else 0.0
            records.append({"step": t, "alive": alive, "avgwealth": avgw})
        return records

# -----------------------
# Funzione per una singola simulation run
# -----------------------
def single_run(rep_idx, lam, p_loss, safe_reward, steps, N, gain, loss, stress_prob, stress_multiplier, stress_duration):
    env = {"p_loss": p_loss, "safe_reward": safe_reward}
    model = ModelMinimal(N=N, lambda_level=lam, env_params=env, steps=steps,
                         gain=gain, loss=loss,
                         stress_prob=stress_prob,
                         stress_multiplier=stress_multiplier,
                         stress_duration=stress_duration)
    recs = model.run()
    # arricchisci i record con metadati
    for r in recs:
        r.update({"rep": rep_idx, "lambda": lam, "p_loss": p_loss, "safe_reward": safe_reward})
    return recs

# -----------------------
# Parametri sweep: personalizzali qui
# -----------------------
LAMBDAS = [DEFAULTS["lambda_low"], DEFAULTS["lambda_typical"], DEFAULTS["lambda_high"]]
P_LOSSES = [DEFAULTS["env_stable"]["p_loss"], 0.25, DEFAULTS["env_unstable"]["p_loss"]]
SAFE_RS = [DEFAULTS["env_stable"]["safe_reward"], DEFAULTS["env_unstable"]["safe_reward"]]
REPS = 40
STEPS = DEFAULTS["steps"]
N = DEFAULTS["N"]

# output files
OUT_FULL = "sweep_full.csv"
OUT_SUM = "sweep_summary.csv"

# -----------------------
# Run sweep (parallel)
# -----------------------
def run_experiment():
    combos = list(product(range(REPS), LAMBDAS, P_LOSSES, SAFE_RS))
    print(f"Total runs: {len(combos)}")
    tasks = []
    for rep_idx, lam, p_loss, safe_reward in combos:
        tasks.append((rep_idx, lam, p_loss, safe_reward))

    # Use multiprocessing Pool to parallelize (optional)
    with Pool() as pool:
        func = partial(_run_task, steps=STEPS, N=N,
                       gain=DEFAULTS["gain"], loss=DEFAULTS["loss"],
                       stress_prob=DEFAULTS["stress_prob"],
                       stress_multiplier=DEFAULTS["stress_multiplier"],
                       stress_duration=DEFAULTS["stress_duration"])
        results = pool.starmap(func, tasks)

    # Flatten and save full CSV
    flat = [item for sub in results for item in sub]
    df_full = pd.DataFrame(flat)
    df_full.to_csv(OUT_FULL, index=False)

    # Summary: mean+std over reps per combo and step  (we aggregate across reps)
    summary = df_full.groupby(["lambda", "p_loss", "safe_reward", "step"]).agg(
        avgwealth_mean=("avgwealth", "mean"),
        avgwealth_std=("avgwealth", "std"),
        alive_mean=("alive", "mean"),
        alive_std=("alive", "std")
    ).reset_index()
    summary.to_csv(OUT_SUM, index=False)
    print(f"Saved {OUT_FULL} and {OUT_SUM}")

def _run_task(rep_idx, lam, p_loss, safe_reward, steps, N, gain, loss, stress_prob, stress_multiplier, stress_duration):
    return single_run(rep_idx, lam, p_loss, safe_reward, steps, N, gain, loss, stress_prob, stress_multiplier, stress_duration)

if __name__ == "__main__":
    run_experiment()
