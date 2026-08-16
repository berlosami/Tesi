import os
import random

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from model import DelayDiscountingModel
from environments import get_environment


# ============================================================
# CONFIGURAZIONE
# ============================================================

N_AGENTS = 100
N_REPLICATES = 10
N_STEPS = 110

RESULTS_DIR = "analysis_results"

os.makedirs(
    RESULTS_DIR,
    exist_ok=True,
)


# ============================================================
# AMBIENTI
# ============================================================

ENVIRONMENTS = {
    "Stable": "stable",
    "Volatile": "volatile",
    "Harsh": "harsh",
}


# ============================================================
# COLORI
# ============================================================

AGENT_COLORS = {
    "impulsive": "red",
    "intermediate": "gold",
    "patient": "green",
}


# ============================================================
# CLASSIFICAZIONE λ
# ============================================================

def classify_lambda(lam):

    if pd.isna(lam):
        return "unknown"

    lam = float(lam)

    if not np.isfinite(lam):
        return "unknown"

    if lam < 0.20:
        return "impulsive"

    if lam < 0.35:
        return "intermediate"

    return "patient"


# ============================================================
# ESECUZIONE SINGOLA REPLICA
# ============================================================

def run_single(
    environment_name,
    seed,
):

    random.seed(seed)
    np.random.seed(seed)

    environment = get_environment(
        environment_name
    )

    model = DelayDiscountingModel(
        environment=environment,
        width=20,
        height=20,
        n_agents=N_AGENTS,
        seed=seed,
    )

    model_records = []
    agent_records = []

    # --------------------------------------------------------
    # STEP 0
    # --------------------------------------------------------

    collect_model_data(
        model,
        step=0,
        model_records=model_records,
    )

    collect_agent_data(
        model,
        step=0,
        replicate=seed,
        environment_name=environment.NAME,
        agent_records=agent_records,
    )

    # --------------------------------------------------------
    # SIMULAZIONE
    # --------------------------------------------------------

    for step in range(
        1,
        N_STEPS + 1,
    ):

        model.step()

        collect_model_data(
            model,
            step=step,
            model_records=model_records,
        )

        collect_agent_data(
            model,
            step=step,
            replicate=seed,
            environment_name=environment.NAME,
            agent_records=agent_records,
        )

    # --------------------------------------------------------
    # DEATH RECORDS
    #
    # Copia diretta dal modello.
    # --------------------------------------------------------

    death_records = []

    for record in model.death_records:

        row = record.copy()

        row["Environment"] = environment.NAME
        row["Replicate"] = seed

        death_records.append(row)

    return (
        pd.DataFrame(model_records),
        pd.DataFrame(agent_records),
        death_records,
    )


# ============================================================
# MODEL DATA
# ============================================================

def collect_model_data(
    model,
    step,
    model_records,
):

    agents = list(
        model.schedule.agents
    )

    alive_agents = [
        agent
        for agent in agents
        if agent.alive
    ]

    population = len(
        alive_agents
    )

    if population:

        energies = [
            agent.energy
            for agent in alive_agents
        ]

        lambdas = [
            agent.lambda_value
            for agent in alive_agents
            if not pd.isna(
                agent.lambda_value
            )
        ]

        mean_energy = float(
            np.mean(energies)
        )

        if lambdas:

            mean_lambda = float(
                np.mean(lambdas)
            )

            if len(lambdas) > 1:

                lambda_variance = float(
                    np.var(
                        lambdas,
                        ddof=1,
                    )
                )

            else:

                lambda_variance = 0.0

        else:

            mean_lambda = np.nan
            lambda_variance = np.nan

    else:

        mean_energy = np.nan
        mean_lambda = np.nan
        lambda_variance = np.nan

    model_records.append(
        {
            "Step": step,
            "Population": population,
            "MeanEnergy": mean_energy,
            "MeanLambda": mean_lambda,
            "LambdaVariance": lambda_variance,
        }
    )


# ============================================================
# AGENT DATA
# ============================================================

def collect_agent_data(
    model,
    step,
    replicate,
    environment_name,
    agent_records,
):

    for agent in model.schedule.agents:

        lam = agent.lambda_value

        # ----------------------------------------------------
        # CONTROLLO λ
        # ----------------------------------------------------

        if lam is None or pd.isna(lam):

            raise RuntimeError(
                f"λ mancante per agente "
                f"{agent.unique_id} "
                f"alla replica {replicate}, "
                f"step {step}."
            )

        strategy = classify_lambda(
            lam
        )

        agent_records.append(
            {
                "Environment":
                    environment_name,

                "Replicate":
                    replicate,

                "Step":
                    step,

                "AgentID":
                    agent.unique_id,

                "Age":
                    agent.age,

                "Lambda":
                    lam,

                "Strategy":
                    strategy,

                "Energy":
                    agent.energy,

                "Alive":
                    agent.alive,

                "Choice":
                    agent.last_choice,

                "Reward":
                    agent.last_reward,

                "DeathCause":
                    agent.death_cause,

                "DeathAge":
                    agent.death_age,

                "DeathEnergy":
                    agent.death_energy,
            }
        )


# ============================================================
# TRE AMBIENTI
# ============================================================

def run_three_environments():

    print()
    print("=" * 60)
    print("TRE AMBIENTI")
    print("=" * 60)

    print()
    print(
        f"Repliche per ambiente: "
        f"{N_REPLICATES}"
    )

    print(
        f"Agenti per replica:    "
        f"{N_AGENTS}"
    )

    print()

    all_model_data = []
    all_agent_data = []
    all_deaths = []

    for (
        environment_label,
        environment_name,
    ) in ENVIRONMENTS.items():

        print(
            f"Simulazione: "
            f"{environment_label}"
        )

        for replicate in range(
            N_REPLICATES
        ):

            # Seed diverso per ogni
            # ambiente e replica.
            seed = (
                replicate
                + (
                    list(
                        ENVIRONMENTS.keys()
                    ).index(
                        environment_label
                    )
                    * 1000
                )
            )

            (
                model_data,
                agent_data,
                death_records,
            ) = run_single(
                environment_name,
                seed,
            )

            model_data[
                "Environment"
            ] = environment_label

            model_data[
                "Replicate"
            ] = replicate

            agent_data[
                "Environment"
            ] = environment_label

            agent_data[
                "Replicate"
            ] = replicate

            all_model_data.append(
                model_data
            )

            all_agent_data.append(
                agent_data
            )

            all_deaths.extend(
                death_records
            )

    model_data = pd.concat(
        all_model_data,
        ignore_index=True,
    )

    agent_data = pd.concat(
        all_agent_data,
        ignore_index=True,
    )

    deaths = pd.DataFrame(
        all_deaths
    )

    # --------------------------------------------------------
    # Controllo finale
    # --------------------------------------------------------

    if not agent_data.empty:

        if agent_data[
            "Lambda"
        ].isna().any():

            raise RuntimeError(
                "ERRORE: sono presenti "
                "lambda mancanti "
                "in agent_data."
            )

    return (
        model_data,
        agent_data,
        deaths,
    )


# ============================================================
# SALVATAGGIO
# ============================================================

def save_csv_files(
    model_data,
    agent_data,
    deaths,
):

    model_path = os.path.join(
        RESULTS_DIR,
        "model_data.csv",
    )

    agent_path = os.path.join(
        RESULTS_DIR,
        "agent_data.csv",
    )

    deaths_path = os.path.join(
        RESULTS_DIR,
        "death_records.csv",
    )

    model_data.to_csv(
        model_path,
        index=False,
    )

    agent_data.to_csv(
        agent_path,
        index=False,
    )

    deaths.to_csv(
        deaths_path,
        index=False,
    )

    print()
    print("=" * 60)
    print("CSV SALVATI")
    print("=" * 60)

    print(model_path)
    print(agent_path)
    print(deaths_path)


# ============================================================
# GRAFICO 1
# POPOLAZIONE
# ============================================================

def plot_population(
    model_data,
):

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    grouped = (
        model_data
        .groupby(
            [
                "Environment",
                "Step",
            ],
            as_index=False,
        )
        ["Population"]
        .mean()
    )

    for environment in (
        ENVIRONMENTS.keys()
    ):

        data = grouped[
            grouped["Environment"]
            == environment
        ]

        if data.empty:
            continue

        ax.plot(
            data["Step"],
            data["Population"],
            label=environment,
        )

    ax.set_xlabel(
        "Età / Step"
    )

    ax.set_ylabel(
        "Agenti vivi"
    )

    ax.set_title(
        "Sopravvivenza della popolazione"
    )

    ax.legend()

    ax.grid(
        alpha=0.3
    )

    fig.tight_layout()

    fig.savefig(
        os.path.join(
            RESULTS_DIR,
            "population_over_time.png",
        ),
        dpi=150,
    )

    plt.close(fig)


# ============================================================
# GRAFICO 2
# DISTRIBUZIONE DELLE CATEGORIE
# ============================================================

def plot_strategy_population(
    agent_data,
):

    grouped = (
        agent_data
        .groupby(
            [
                "Environment",
                "Step",
                "Strategy",
            ],
            as_index=False,
        )
        .size()
    )

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(10, 12),
        sharex=True,
    )

    for ax, environment in zip(
        axes,
        ENVIRONMENTS.keys(),
    ):

        data = grouped[
            grouped["Environment"]
            == environment
        ]

        for strategy in [
            "impulsive",
            "intermediate",
            "patient",
        ]:

            strategy_data = data[
                data["Strategy"]
                == strategy
            ]

            if strategy_data.empty:
                continue

            ax.plot(
                strategy_data["Step"],
                strategy_data["size"],
                label=strategy,
                color=AGENT_COLORS[
                    strategy
                ],
            )

        ax.set_title(
            environment
        )

        ax.set_ylabel(
            "Agenti"
        )

        ax.grid(
            alpha=0.3
        )

        handles, labels = (
            ax.get_legend_handles_labels()
        )

        if handles:
            ax.legend()

    axes[-1].set_xlabel(
        "Età / Step"
    )

    fig.tight_layout()

    fig.savefig(
        os.path.join(
            RESULTS_DIR,
            "strategy_population.png",
        ),
        dpi=150,
    )

    plt.close(fig)


# ============================================================
# GRAFICO 3
# ENERGIA MEDIA
# ============================================================

def plot_energy(
    model_data,
):

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(10, 12),
        sharex=True,
    )

    for ax, environment in zip(
        axes,
        ENVIRONMENTS.keys(),
    ):

        data = model_data[
            model_data["Environment"]
            == environment
        ]

        grouped = (
            data
            .groupby(
                "Step",
                as_index=False,
            )["MeanEnergy"]
            .mean()
        )

        ax.plot(
            grouped["Step"],
            grouped["MeanEnergy"],
        )

        ax.set_title(
            environment
        )

        ax.set_ylabel(
            "Energia media"
        )

        ax.grid(
            alpha=0.3
        )

    axes[-1].set_xlabel(
        "Età / Step"
    )

    fig.tight_layout()

    fig.savefig(
        os.path.join(
            RESULTS_DIR,
            "mean_energy.png",
        ),
        dpi=150,
    )

    plt.close(fig)


# ============================================================
# GRAFICO 4
# MORTI PER CAUSA
# ============================================================

def plot_deaths_by_cause(deaths):

    if deaths.empty:
        print("Nessun decesso registrato.")
        return

    if "DeathCause" not in deaths.columns:
        print("ERRORE: manca la colonna 'DeathCause'.")
        return

    grouped = (
        deaths
        .groupby(
            ["Environment", "DeathCause"],
            as_index=False,
        )
        .size()
    )

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(10, 10),
    )

    for ax, environment in zip(
        axes,
        ENVIRONMENTS.keys(),
    ):

        data = grouped[
            grouped["Environment"] == environment
        ]

        if data.empty:
            ax.set_title(
                f"{environment} - nessun decesso"
            )
            continue

        ax.bar(
            data["DeathCause"].astype(str),
            data["size"],
        )

        ax.set_title(
            f"Morti per causa - {environment}"
        )

        ax.set_ylabel("Morti")
        ax.grid(
            axis="y",
            alpha=0.3,
        )

    axes[-1].set_xlabel("Causa")

    fig.tight_layout()

    fig.savefig(
        os.path.join(
            RESULTS_DIR,
            "deaths_by_cause.png",
        ),
        dpi=150,
    )

    plt.close(fig)


# ============================================================
# GRAFICO 5
# MORTE: ETÀ + STRATEGIA
# ============================================================

def plot_deaths_by_age_strategy(
    deaths,
):

    if deaths.empty:
        return

    if "Age" not in deaths.columns:
        return

    if "Strategy" not in deaths.columns:
        return

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(10, 12),
        sharex=True,
    )

    for ax, environment in zip(
        axes,
        ENVIRONMENTS.keys(),
    ):

        data = deaths[
            deaths["Environment"]
            == environment
        ]

        for strategy in [
            "impulsive",
            "intermediate",
            "patient",
        ]:

            strategy_data = data[
                data["Strategy"]
                == strategy
            ]

            if strategy_data.empty:
                continue

            counts = (
                strategy_data
                .groupby("Age")
                .size()
            )

            ax.plot(
                counts.index,
                counts.values,
                marker="o",
                label=strategy,
                color=AGENT_COLORS[
                    strategy
                ],
            )

        ax.set_title(
            f"Morti per età - {environment}"
        )

        ax.set_ylabel(
            "Morti"
        )

        ax.grid(
            alpha=0.3
        )

        handles, labels = (
            ax.get_legend_handles_labels()
        )

        if handles:
            ax.legend()

    axes[-1].set_xlabel(
        "Età alla morte"
    )

    fig.tight_layout()

    fig.savefig(
        os.path.join(
            RESULTS_DIR,
            "deaths_by_age_strategy.png",
        ),
        dpi=150,
    )

    plt.close(fig)


# ============================================================
# GRAFICO 6
# ETÀ + ENERGIA ALLA MORTE
# ============================================================

def plot_death_age_energy(
    deaths,
):

    if deaths.empty:
        return

    if "Age" not in deaths.columns:
        return

    if "Energy" not in deaths.columns:
        return

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(10, 12),
    )

    for ax, environment in zip(
        axes,
        ENVIRONMENTS.keys(),
    ):

        data = deaths[
            deaths["Environment"]
            == environment
        ]

        for strategy in [
            "impulsive",
            "intermediate",
            "patient",
        ]:

            strategy_data = data[
                data["Strategy"]
                == strategy
            ]

            if strategy_data.empty:
                continue

            ax.scatter(
                strategy_data["Age"],
                strategy_data["Energy"],
                label=strategy,
                color=AGENT_COLORS[
                    strategy
                ],
                alpha=0.7,
            )

        ax.axhline(
            0,
            linestyle="--",
            linewidth=1,
        )

        ax.set_title(
            f"Età ed energia alla morte - "
            f"{environment}"
        )

        ax.set_ylabel(
            "Energia alla morte"
        )

        ax.grid(
            alpha=0.3
        )

        handles, labels = (
            ax.get_legend_handles_labels()
        )

        if handles:
            ax.legend()

    axes[-1].set_xlabel(
        "Età alla morte"
    )

    fig.tight_layout()

    fig.savefig(
        os.path.join(
            RESULTS_DIR,
            "death_age_energy.png",
        ),
        dpi=150,
    )

    plt.close(fig)


# ============================================================
# TABELLA DECESSI
# ============================================================

def save_death_summary(
    deaths,
):

    if deaths.empty:
        return

    summary = (
        deaths
        .groupby(
            [
                "Environment",
                "DeathCause",
                "Strategy",
            ],
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "size": "Deaths"
            }
        )
    )

    summary.to_csv(
        os.path.join(
            RESULTS_DIR,
            "death_summary.csv",
        ),
        index=False,
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    (
        model_data,
        agent_data,
        deaths,
    ) = run_three_environments()

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    save_csv_files(
        model_data,
        agent_data,
        deaths,
    )

    # --------------------------------------------------------
    # GRAFICI
    # --------------------------------------------------------

    plot_population(
        model_data
    )

    plot_strategy_population(
        agent_data
    )

    plot_energy(
        model_data
    )

    plot_deaths_by_cause(
        deaths
    )

    plot_deaths_by_age_strategy(
        deaths
    )

    plot_death_age_energy(
        deaths
    )

    save_death_summary(
        deaths
    )

    # --------------------------------------------------------
    # CONTROLLO RISULTATI
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("CONTROLLO DATI")
    print("=" * 60)

    print()

    print(
        "Righe model_data:",
        len(model_data),
    )

    print(
        "Righe agent_data:",
        len(agent_data),
    )

    print(
        "Death records:",
        len(deaths),
    )

    print()

    print(
        "Strategie agent_data:"
    )

    print(
        agent_data[
            "Strategy"
        ].value_counts(
            dropna=False
        )
    )

    print()

    print(
        "Lambda mancanti:",
        agent_data[
            "Lambda"
        ].isna().sum(),
    )

    print()

    if not deaths.empty:

        print(
            "Morti per ambiente:"
        )

        print(
            deaths[
                "Environment"
            ].value_counts()
        )

        print()

        print(
            "Morti per causa:"
        )

        print(
            deaths[
                "DeathCause"
            ].value_counts()
        )

    else:

        print(
            "Nessun decesso registrato."
        )

    print()
    print("=" * 60)
    print(
        "ANALISI COMPLETATA"
    )
    print("=" * 60)

    print()
    print(
        f"Risultati in: "
        f"{RESULTS_DIR}/"
    )