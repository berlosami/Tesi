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
        return "patient"

    if lam < 0.35:
        return "intermediate"

    return "impulsive"


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

    agents = list(model.schedule.agents)

    alive_agents = [
        agent
        for agent in agents
        if agent.alive
    ]

    population = len(alive_agents)

    impulsive_agents = [
        agent for agent in alive_agents
        if agent.lambda_value >= 0.35
    ]

    intermediate_agents = [
        agent for agent in alive_agents
        if 0.20 <= agent.lambda_value < 0.35
    ]

    patient_agents = [
        agent for agent in alive_agents
        if agent.lambda_value < 0.20
    ]

    impulsive = len(impulsive_agents)
    intermediate = len(intermediate_agents)
    patient = len(patient_agents)

    if population:

        energies = [
            agent.energy
            for agent in alive_agents
        ]

        lambdas = [
            agent.lambda_value
            for agent in alive_agents
            if not pd.isna(agent.lambda_value)
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

    impulsive_agents = [
        agent for agent in alive_agents
        if agent.lambda_value >= 0.35
    ]

    intermediate_agents = [
        agent for agent in alive_agents
        if 0.20 <= agent.lambda_value < 0.35
    ]

    patient_agents = [
        agent for agent in alive_agents
        if agent.lambda_value < 0.20
    ]

    impulsive = len(impulsive_agents)
    intermediate = len(intermediate_agents)
    patient = len(patient_agents)

    impulsive_mean_energy = (
        np.mean([agent.energy for agent in impulsive_agents])
        if impulsive_agents else np.nan
    )

    intermediate_mean_energy = (
        np.mean([agent.energy for agent in intermediate_agents])
        if intermediate_agents else np.nan
    )

    patient_mean_energy = (
        np.mean([agent.energy for agent in patient_agents])
        if patient_agents else np.nan
    )

    model_records.append(
        {
            "Step": step,
            "Population": population,
            "Impulsive": impulsive,
            "Intermediate": intermediate,
            "Patient": patient,
            "MeanEnergy": mean_energy,
            "ImpulsiveMeanEnergy":
                float(impulsive_mean_energy)
                if not pd.isna(impulsive_mean_energy)
                else np.nan,
            "IntermediateMeanEnergy":
                float(intermediate_mean_energy)
                if not pd.isna(intermediate_mean_energy)
                else np.nan,
            "PatientMeanEnergy":
                float(patient_mean_energy)
                if not pd.isna(patient_mean_energy)
                else np.nan,
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
# POPOLAZIONE TOTALE + IMPULSIVI + INTERMEDI + PAZIENTI
# UN GRAFICO PER OGNI AMBIENTE
# ============================================================

def plot_population(
    model_data,
):
    

    for environment in ENVIRONMENTS.keys():

        data = model_data[
            model_data["Environment"]
            == environment
        ].copy()

        if data.empty:
            continue

        grouped = (
            data
            .groupby(
                "Step",
                as_index=False,
            )[
                [
                    "Population",
                    "Impulsive",
                    "Intermediate",
                    "Patient",
                ]
            ]
            .mean(numeric_only=True)
        )

        fig, ax = plt.subplots(
            figsize=(10, 6)
        )

        # ----------------------------------------------------
        # POPOLAZIONE TOTALE
        # ----------------------------------------------------

        ax.plot(
            grouped["Step"],
            grouped["Population"],
            label="Popolazione totale",
            linewidth=2,
        )

        # ----------------------------------------------------
        # IMPULSIVI
        # ----------------------------------------------------

        ax.plot(
            grouped["Step"],
            grouped["Impulsive"],
            label="Impulsivi",
            linewidth=2,
            color=AGENT_COLORS["impulsive"],
        )

        # ----------------------------------------------------
        # INTERMEDI
        # ----------------------------------------------------

        ax.plot(
            grouped["Step"],
            grouped["Intermediate"],
            label="Intermedi",
            linewidth=2,
            color=AGENT_COLORS["intermediate"],
        )

        # ----------------------------------------------------
        # PAZIENTI
        # ----------------------------------------------------

        ax.plot(
            grouped["Step"],
            grouped["Patient"],
            label="Pazienti",
            linewidth=2,
            color=AGENT_COLORS["patient"],
        )

        # ----------------------------------------------------
        # LABEL E TITOLO
        # ----------------------------------------------------

        ax.set_xlabel(
            "Età / Step"
        )
        ax.set_xlim(0, 110)

        ax.set_ylabel(
            "Agenti vivi"
        )

        ax.set_title(
            f"Sopravvivenza e composizione della popolazione - {environment}"
        )

        ax.legend()

        ax.grid(
            alpha=0.3
        )

        fig.tight_layout()

        fig.savefig(
            os.path.join(
                RESULTS_DIR,
                f"population_{environment.lower()}.png",
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
# GRAFICO
# ENERGIA MEDIA PER CLASSE DI λ
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

    classes = [
        (
            "ImpulsiveMeanEnergy",
            "Impulsivi (λ ≥ 0.35)",
        ),
        (
            "IntermediateMeanEnergy",
            "Intermedi (0.20 ≤ λ < 0.35)",
        ),
        (
            "PatientMeanEnergy",
            "Pazienti (λ < 0.20)",
        ),
    ]

    for ax, environment in zip(
        axes,
        ENVIRONMENTS.keys(),
    ):

        data = model_data[
            model_data["Environment"]
            == environment
        ]

        if data.empty:
            continue

        grouped = (
            data
            .groupby(
                "Step",
                as_index=False,
            )[
                [
                    "ImpulsiveMeanEnergy",
                    "IntermediateMeanEnergy",
                    "PatientMeanEnergy",
                ]
            ]
            .mean(numeric_only=True)
        )

        for column, label in classes:

            if column == "ImpulsiveMeanEnergy":
               color = AGENT_COLORS["impulsive"]

            elif column == "IntermediateMeanEnergy":
                color = AGENT_COLORS["intermediate"]

            else:
               color = AGENT_COLORS["patient"]

            ax.plot(
                  grouped["Step"],
                  grouped[column],
                  label=label,
                  color=color,
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

        ax.legend()

    axes[-1].set_xlabel(
        "Età / Step"
    )

    fig.suptitle(
        "Energia media degli agenti vivi per classe di impulsività",
        fontsize=14,
    )

    fig.tight_layout()

    fig.savefig(
        os.path.join(
            RESULTS_DIR,
            "mean_energy_by_lambda_class.png",
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