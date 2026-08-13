import matplotlib.pyplot as plt
import pandas as pd
from NEW_baseline_model import BaselineModel
from NEW_uniform_mortality_model import UniformMortalityModel
from NEW_age_dependent_model import AgeDependentMortalityModel

T = 120
SEED = 123
MORTALITY_SCALES = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]

def run_model(model):
    for _ in range(T):
        model.step()
    return model

# BASELINE
baseline = run_model(BaselineModel(seed=SEED))
baseline_df = baseline.datacollector.get_model_vars_dataframe()
print("\nBASELINE")
print("Energia pazienti:", baseline_df["Mean Energy Patient"].iloc[-1])
print("Energia impulsivi:", baseline_df["Mean Energy Impulsive"].iloc[-1])

# UNIFORM MORTALITY SWEEP
rows = []
for scale in MORTALITY_SCALES:
    model = run_model(UniformMortalityModel(
        mortality_scale=scale,
        seed=SEED + int(scale * 1000)
    ))
    df = model.datacollector.get_model_vars_dataframe()
    rows.append({
        "mortality_scale": scale,
        "final_population": df["Population"].iloc[-1],
        "final_mean_energy": df["Mean Energy"].iloc[-1],
        "final_mean_energy_patient": df["Mean Energy Patient"].iloc[-1],
        "final_mean_energy_impulsive": df["Mean Energy Impulsive"].iloc[-1],
        "final_lambda_x100": df["Mean Lambda x100"].iloc[-1],
        "final_lambda_variance_x1000": df["Lambda Variance x1000"].iloc[-1],
        "patient_fraction": df["Patient Fraction"].iloc[-1],
        "impulsive_fraction": df["Impulsive Fraction"].iloc[-1],
        "deaths_patient": df["Deaths Patient"].iloc[-1],
        "deaths_impulsive": df["Deaths Impulsive"].iloc[-1],
    })
uniform_results = pd.DataFrame(rows)
print("\nUNIFORM MORTALITY")
print(uniform_results.to_string(index=False))

# AGE-DEPENDENT MORTALITY
age_model = run_model(AgeDependentMortalityModel(seed=SEED))
age_df = age_model.datacollector.get_model_vars_dataframe()
print("\nAGE-DEPENDENT MORTALITY")
print("Popolazione:", age_df["Population"].iloc[-1])
print("Patient fraction:", age_df["Patient Fraction"].iloc[-1])
print("Impulsive fraction:", age_df["Impulsive Fraction"].iloc[-1])
print("Mean lambda x100:", age_df["Mean Lambda x100"].iloc[-1])

# BASELINE PLOT
plt.figure()
plt.plot(baseline_df.index + 1, baseline_df["Mean Energy Patient"], label="Paziente")
plt.plot(baseline_df.index + 1, baseline_df["Mean Energy Impulsive"], label="Impulsivo")
plt.xlabel("Anno"); plt.ylabel("Energia media")
plt.title("Baseline: energia per strategia"); plt.legend(); plt.tight_layout(); plt.show()

# UNIFORM PLOTS
plt.figure()
plt.plot(uniform_results["mortality_scale"], uniform_results["patient_fraction"], marker="o", label="Paziente")
plt.plot(uniform_results["mortality_scale"], uniform_results["impulsive_fraction"], marker="o", label="Impulsivo")
plt.axhline(0.5, linestyle="--")
plt.xlabel("Mortality scale"); plt.ylabel("Frazione finale")
plt.title("Uniform mortality: composizione"); plt.legend(); plt.tight_layout(); plt.show()

plt.figure()
plt.plot(uniform_results["mortality_scale"], uniform_results["final_lambda_x100"], marker="o")
plt.xlabel("Mortality scale"); plt.ylabel("Mean lambda ×100")
plt.title("Uniform mortality: lambda medio"); plt.tight_layout(); plt.show()

plt.figure()
plt.plot(uniform_results["mortality_scale"], uniform_results["final_lambda_variance_x1000"], marker="o")
plt.xlabel("Mortality scale"); plt.ylabel("Lambda variance ×1000")
plt.title("Uniform mortality: varianza lambda"); plt.tight_layout(); plt.show()

plt.figure()
plt.plot(uniform_results["mortality_scale"], uniform_results["deaths_patient"], marker="o", label="Pazienti")
plt.plot(uniform_results["mortality_scale"], uniform_results["deaths_impulsive"], marker="o", label="Impulsivi")
plt.xlabel("Mortality scale"); plt.ylabel("Morti")
plt.title("Uniform mortality: morti per strategia"); plt.legend(); plt.tight_layout(); plt.show()

# AGE-DEPENDENT PLOTS
years = age_df.index + 1

plt.figure()
plt.plot(years, age_df["Population"])
plt.xlabel("Anno"); plt.ylabel("Popolazione viva")
plt.title("Age-dependent mortality: popolazione"); plt.tight_layout(); plt.show()

plt.figure()
plt.plot(years, age_df["Patient Fraction"], label="Paziente")
plt.plot(years, age_df["Impulsive Fraction"], label="Impulsivo")
plt.axhline(0.5, linestyle="--")
plt.xlabel("Anno"); plt.ylabel("Frazione")
plt.title("Age-dependent mortality: composizione"); plt.legend(); plt.tight_layout(); plt.show()

plt.figure()
plt.plot(years, age_df["Mean Lambda x100"])
plt.xlabel("Anno"); plt.ylabel("Mean lambda ×100")
plt.title("Age-dependent mortality: lambda medio"); plt.tight_layout(); plt.show()

plt.figure()
plt.plot(years, age_df["Lambda Variance x1000"])
plt.xlabel("Anno"); plt.ylabel("Lambda variance ×1000")
plt.title("Age-dependent mortality: varianza lambda"); plt.tight_layout(); plt.show()

plt.figure()
plt.plot(years, age_df["Mean Energy Patient"], label="Paziente")
plt.plot(years, age_df["Mean Energy Impulsive"], label="Impulsivo")
plt.xlabel("Anno"); plt.ylabel("Energia media")
plt.title("Age-dependent mortality: energia"); plt.legend(); plt.tight_layout(); plt.show()

uniform_results.to_csv("NEW_uniform_mortality_results.csv", index=False)
age_df.to_csv("NEW_age_dependent_timeseries.csv")
baseline_df.to_csv("NEW_baseline_timeseries.csv")
print("\nCSV salvati.")
