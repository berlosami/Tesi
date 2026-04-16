import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from model_environment_impulsivity import SurvivalModel, PARAMS


environments = ["stable", "volatile", "harsh"]
colors = {"stable": "blue", "volatile": "orange", "harsh": "red"}

fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True)

lambda_bins = np.linspace(0.05, 0.50, 30)


# -------------------------
# LOOP AMBIENTI
# -------------------------
for ax, env in zip(axes, environments):

    params = PARAMS.copy()
    params["ENVIRONMENT"] = env

    model = SurvivalModel(params)

    for t in range(params["T"]):
        model.step()

    df = model.datacollector.get_agent_vars_dataframe().reset_index()

    df = df[df["Alive"] == True]

    df["LambdaRound"] = df["Lambda"].round(2)

    grouped = df.groupby(
        ["Step", "LambdaRound"]
    ).size().reset_index(name="Count")

    ax.scatter(
        grouped["LambdaRound"],
        grouped["Step"],
        s=grouped["Count"] * 10,
        alpha=0.6,
        color=colors[env]
    )

    ax.set_title(env.capitalize())
    ax.grid(True)

    ax.set_xlabel("Lambda")


axes[0].set_ylabel("Time (Days)")


# -------------------------
# LEGGENDA SIZE
# -------------------------
for size in [1, 5, 10, 20]:

    plt.scatter([], [], s=size * 10, c="gray", alpha=0.5,
                label=f"{size} agents")


fig.legend(title="Bubble size (agents)", loc="upper right")

plt.suptitle("Survival Dynamics Across Environments", fontsize=16)

plt.tight_layout()
plt.savefig("3_environments_subplot.png", dpi=300)

print("Saved: 3_environments_subplot.png")