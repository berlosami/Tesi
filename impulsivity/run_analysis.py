import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from environments import (
    SCENARIOS,
    create_environment,
)
from model import (
    DelayDiscountingModel,
    INITIAL_AGE,
    N_AGENTS,
    N_STEPS,
)


# ============================================================
# ANALYSIS PARAMETERS
# ============================================================

N_REPLICATES = 10

OUTPUT_DIR = "analysis_results"

MODEL_DATA_FILE = "model_data.csv"
AGENT_DATA_FILE = "agent_data.csv"
DEATH_DATA_FILE = "death_records.csv"

SURVIVAL_REPLICATE_FILE = "survival_by_replicate.csv"
SURVIVAL_SUMMARY_FILE = "survival_summary.csv"
ENERGY_SUMMARY_FILE = "energy_summary.csv"
DEATH_SUMMARY_FILE = "death_summary.csv"
SCENARIO_SUMMARY_FILE = "scenario_summary.csv"


# ============================================================
# HELPERS
# ============================================================

def safe_filename(name):

    return re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        name,
    )


def ensure_output_directory():

    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# RUN ONE REPLICATE
# ============================================================

def run_single(environment_name, replicate, seed):

    environment = create_environment(environment_name)

    model = DelayDiscountingModel(
        environment=environment,
        n_agents=N_AGENTS,
        seed=seed,
    )

    model.run_model(N_STEPS)

    # --------------------------------------------------------
    # MODEL DATA
    # --------------------------------------------------------

    model_data = model.datacollector.get_model_vars_dataframe()

    model_data = model_data.reset_index()

    if "Step" not in model_data.columns:
        model_data = model_data.rename(
            columns={"index": "Step"}
        )

    model_data["Age"] = INITIAL_AGE + model_data["Step"]

    model_data["Environment"] = environment.name
    model_data["ScenarioType"] = environment.scenario_type
    model_data["Replicate"] = replicate

    model_data["R1"] = environment.R1
    model_data["R2"] = environment.R2
    model_data["D2"] = environment.D2
    model_data["LambdaCutoff"] = environment.lambda_cutoff
    model_data["MetabolicCost"] = environment.metabolic_cost
    model_data["P_R2_Success"] = environment.p_r2_success

    # --------------------------------------------------------
    # AGENT DATA
    # --------------------------------------------------------

    agent_data = model.datacollector.get_agent_vars_dataframe()

    agent_data = agent_data.reset_index()

    agent_data["Age"] = agent_data["Age"].astype(float)

    agent_data["Environment"] = environment.name
    agent_data["ScenarioType"] = environment.scenario_type
    agent_data["Replicate"] = replicate

    agent_data["R2"] = environment.R2
    agent_data["LambdaCutoff"] = environment.lambda_cutoff
    agent_data["MetabolicCost"] = environment.metabolic_cost
    agent_data["P_R2_Success"] = environment.p_r2_success

    # --------------------------------------------------------
    # DEATH DATA
    # --------------------------------------------------------

    death_data = pd.DataFrame(model.death_records)

    if not death_data.empty:

        death_data["Replicate"] = replicate

    return (
        model_data,
        agent_data,
        death_data,
    )


# ============================================================
# RUN ALL REPLICATES
# ============================================================

def run_all_simulations():

    all_model_data = []
    all_agent_data = []
    all_death_data = []

    scenario_names = list(SCENARIOS.keys())

    print("\n" + "=" * 70)
    print("RUNNING SIMULATIONS")
    print("=" * 70)

    for scenario_index, environment_name in enumerate(
        scenario_names
    ):

        environment = create_environment(environment_name)

        print(
            f"\nScenario {scenario_index + 1}/{len(scenario_names)}:"
        )

        print(environment.description())

        for replicate in range(1, N_REPLICATES + 1):

            seed = (
                scenario_index * 10000
                + replicate
            )

            print(
                f"  Replicate {replicate}/{N_REPLICATES}",
                end="\r",
            )

            (
                model_data,
                agent_data,
                death_data,
            ) = run_single(
                environment_name,
                replicate,
                seed,
            )

            all_model_data.append(model_data)
            all_agent_data.append(agent_data)

            if not death_data.empty:
                all_death_data.append(death_data)

        print()

    model_data = pd.concat(
        all_model_data,
        ignore_index=True,
    )

    agent_data = pd.concat(
        all_agent_data,
        ignore_index=True,
    )

    if all_death_data:

        death_data = pd.concat(
            all_death_data,
            ignore_index=True,
        )

    else:

        death_data = pd.DataFrame(
            columns=[
                "AgentID",
                "Step",
                "Age",
                "Lambda",
                "Strategy",
                "Energy",
                "DeathCause",
                "Environment",
                "ScenarioType",
                "R2",
                "LambdaCutoff",
                "MetabolicCost",
                "P_R2_Success",
                "Replicate",
            ]
        )

    return (
        model_data,
        agent_data,
        death_data,
    )


# ============================================================
# SURVIVAL TABLES
# ============================================================

def create_survival_tables(agent_data):

    # --------------------------------------------------------
    # FINAL STEP
    # --------------------------------------------------------

    final_step = agent_data["Step"].max()

    final_data = agent_data[
        agent_data["Step"] == final_step
    ].copy()

    # Exactly 50 agents of each strategy at the start
    initial_per_strategy = N_AGENTS / 2

    # --------------------------------------------------------
    # SURVIVAL BY REPLICATE
    # --------------------------------------------------------

    survival = (
        final_data
        .groupby(
            [
                "Environment",
                "ScenarioType",
                "Replicate",
                "Strategy",
                "R2",
                "LambdaCutoff",
                "MetabolicCost",
                "P_R2_Success",
            ],
            as_index=False,
        )
        .agg(
            Survivors=("Alive", "sum"),
        )
    )

    survival["InitialN"] = initial_per_strategy

    survival["Deaths"] = (
        survival["InitialN"]
        - survival["Survivors"]
    )

    survival["SurvivalPct"] = (
        survival["Survivors"]
        / survival["InitialN"]
        * 100
    )

    survival["DeathPct"] = (
        survival["Deaths"]
        / survival["InitialN"]
        * 100
    )

    # --------------------------------------------------------
    # DESCRIPTIVE SUMMARY ACROSS 10 REPLICATES
    # --------------------------------------------------------

    summary = (
        survival
        .groupby(
            [
                "Environment",
                "ScenarioType",
                "Strategy",
                "R2",
                "LambdaCutoff",
                "MetabolicCost",
                "P_R2_Success",
            ],
            as_index=False,
        )
        .agg(
            MeanSurvivalPct=(
                "SurvivalPct",
                "mean",
            ),

            SDSurvivalPct=(
                "SurvivalPct",
                "std",
            ),

            MinSurvivalPct=(
                "SurvivalPct",
                "min",
            ),

            MaxSurvivalPct=(
                "SurvivalPct",
                "max",
            ),

            MeanDeathPct=(
                "DeathPct",
                "mean",
            ),
        )
    )

    return survival, summary


# ============================================================
# ENERGY TABLE
# ============================================================

def create_energy_summary(agent_data):

    final_step = agent_data["Step"].max()

    final_alive = agent_data[
        (agent_data["Step"] == final_step)
        &
        (agent_data["Alive"] == True)
    ].copy()

    energy = (
        final_alive
        .groupby(
            [
                "Environment",
                "ScenarioType",
                "Replicate",
                "Strategy",
                "R2",
                "MetabolicCost",
                "P_R2_Success",
            ],
            as_index=False,
        )
        .agg(
            MeanFinalEnergy=("Energy", "mean"),
        )
    )

    summary = (
        energy
        .groupby(
            [
                "Environment",
                "ScenarioType",
                "Strategy",
                "R2",
                "MetabolicCost",
                "P_R2_Success",
            ],
            as_index=False,
        )
        .agg(
            MeanFinalEnergy=(
                "MeanFinalEnergy",
                "mean",
            ),

            SDFinalEnergy=(
                "MeanFinalEnergy",
                "std",
            ),

            MinFinalEnergy=(
                "MeanFinalEnergy",
                "min",
            ),

            MaxFinalEnergy=(
                "MeanFinalEnergy",
                "max",
            ),
        )
    )

    return summary


# ============================================================
# DEATH TABLE
# ============================================================

def create_death_summary(death_data):

    if death_data.empty:
        return pd.DataFrame()

    deaths = (
        death_data
        .groupby(
            [
                "Environment",
                "ScenarioType",
                "Strategy",
                "DeathCause",
            ],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "Deaths"})
    )

    # Percentage relative to the 50 agents initially belonging
    # to each strategy.
    deaths["InitialStrategyN"] = N_AGENTS / 2

    deaths["DeathPct"] = (
        deaths["Deaths"]
        / deaths["InitialStrategyN"]
        * 100
    )

    return deaths


# ============================================================
# SCENARIO SUMMARY
# ============================================================

def create_scenario_summary(
    survival_summary,
    energy_summary,
):

    survival_total = (
        survival_summary
        .groupby(
            [
                "Environment",
                "ScenarioType",
                "R2",
                "LambdaCutoff",
                "MetabolicCost",
                "P_R2_Success",
            ],
            as_index=False,
        )
        .agg(
            MeanSurvivalPct=(
                "MeanSurvivalPct",
                "mean",
            )
        )
    )

    return survival_total


# ============================================================
# SAVE TABLES
# ============================================================

def save_tables(
    model_data,
    agent_data,
    death_data,
    survival,
    survival_summary,
    energy_summary,
    death_summary,
    scenario_summary,
):

    ensure_output_directory()

    model_data.to_csv(
        os.path.join(
            OUTPUT_DIR,
            MODEL_DATA_FILE,
        ),
        index=False,
    )

    agent_data.to_csv(
        os.path.join(
            OUTPUT_DIR,
            AGENT_DATA_FILE,
        ),
        index=False,
    )

    death_data.to_csv(
        os.path.join(
            OUTPUT_DIR,
            DEATH_DATA_FILE,
        ),
        index=False,
    )

    survival.to_csv(
        os.path.join(
            OUTPUT_DIR,
            SURVIVAL_REPLICATE_FILE,
        ),
        index=False,
    )

    survival_summary.to_csv(
        os.path.join(
            OUTPUT_DIR,
            SURVIVAL_SUMMARY_FILE,
        ),
        index=False,
    )

    energy_summary.to_csv(
        os.path.join(
            OUTPUT_DIR,
            ENERGY_SUMMARY_FILE,
        ),
        index=False,
    )

    death_summary.to_csv(
        os.path.join(
            OUTPUT_DIR,
            DEATH_SUMMARY_FILE,
        ),
        index=False,
    )

    scenario_summary.to_csv(
        os.path.join(
            OUTPUT_DIR,
            SCENARIO_SUMMARY_FILE,
        ),
        index=False,
    )


# ============================================================
# PLOT 1
# SURVIVAL PERCENTAGE BY STRATEGY
# ============================================================

def plot_survival_percentage(
    agent_data,
    environment_name,
):

    data = agent_data[
        agent_data["Environment"] == environment_name
    ].copy()

    if data.empty:
        return

    # --------------------------------------------------------
    # FINAL STEP
    # --------------------------------------------------------

    final_step = data["Step"].max()

    final_data = data[
        data["Step"] == final_step
    ].copy()

    # --------------------------------------------------------
    # SURVIVORS BY REPLICATE AND STRATEGY
    # --------------------------------------------------------

    survival = (
        final_data
        .groupby(
            [
                "Replicate",
                "Strategy",
            ],
            as_index=False,
        )
        .agg(
            Survivors=("Alive", "sum")
        )
    )

    # Every strategy starts with exactly 50 agents.
    survival["SurvivalPct"] = (
        survival["Survivors"]
        / 50
        * 100
    )

    # --------------------------------------------------------
    # MEAN ACROSS THE 10 REPLICATES
    # --------------------------------------------------------

    summary = (
        survival
        .groupby(
            "Strategy",
            as_index=False,
        )
        .agg(
            MeanSurvivalPct=(
                "SurvivalPct",
                "mean",
            ),

            SDSurvivalPct=(
                "SurvivalPct",
                "std",
            ),
        )
    )

    # --------------------------------------------------------
    # KEEP ORDER
    # --------------------------------------------------------

    strategy_order = [
        "patient",
        "impulsive",
    ]

    summary["Order"] = summary[
        "Strategy"
    ].map(
        {
            "patient": 0,
            "impulsive": 1,
        }
    )

    summary = (
        summary
        .sort_values("Order")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # BAR CHART
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    x = np.arange(
        len(summary)
    )

    bars = ax.bar(
        x,
        summary["MeanSurvivalPct"],
        width=0.55,
    )

    # --------------------------------------------------------
    # ERROR BARS
    #
    # Descriptive only:
    # standard deviation across the 10 replicates.
    # --------------------------------------------------------

    ax.errorbar(
        x,
        summary["MeanSurvivalPct"],
        yerr=summary["SDSurvivalPct"],
        fmt="none",
        capsize=5,
    )

    # --------------------------------------------------------
    # VALUE LABELS
    # --------------------------------------------------------

    for bar, value in zip(
        bars,
        summary["MeanSurvivalPct"],
    ):

        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 2,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
        )

    # --------------------------------------------------------
    # AXES
    # --------------------------------------------------------

    ax.set_xticks(x)

    ax.set_xticklabels(
        [
            "Patient",
            "Impulsive",
        ]
    )

    ax.set_ylabel(
        "Mean survival (%)"
    )

    ax.set_xlabel(
        "Strategy"
    )

    ax.set_title(
        f"Final survival by strategy\n{environment_name}"
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    filename = (
        "survival_"
        + safe_filename(environment_name)
        + ".png"
    )

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            filename,
        ),
        dpi=300,
    )

    plt.close()


# ============================================================
# PLOT 2
# MEAN ENERGY BY STRATEGY
# ============================================================

def plot_mean_energy(
    agent_data,
    environment_name,
):

    data = agent_data[
        agent_data["Environment"] == environment_name
    ].copy()

    if data.empty:
        return

    alive_data = data[
        data["Alive"] == True
    ]

    grouped = (
        alive_data
        .groupby(
            [
                "Replicate",
                "Step",
                "Age",
                "Strategy",
            ],
            as_index=False,
        )
        .agg(
            MeanEnergy=("Energy", "mean")
        )
    )

    plot_data = (
        grouped
        .groupby(
            [
                "Step",
                "Age",
                "Strategy",
            ],
            as_index=False,
        )
        .agg(
            MeanEnergy=(
                "MeanEnergy",
                "mean",
            )
        )
    )

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )

    for strategy in ["patient", "impulsive"]:

        strategy_data = plot_data[
            plot_data["Strategy"] == strategy
        ]

        if strategy_data.empty:
            continue

        ax.plot(
            strategy_data["Age"],
            strategy_data["MeanEnergy"],
            label=strategy.capitalize(),
        )

    ax.set_title(
        f"Mean energy by strategy - {environment_name}"
    )

    ax.set_xlabel("Age")
    ax.set_ylabel("Mean energy")

    ax.set_xlim(
        INITIAL_AGE,
        INITIAL_AGE + N_STEPS,
    )

    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()

    filename = (
        "energy_"
        + safe_filename(environment_name)
        + ".png"
    )

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            filename,
        ),
        dpi=300,
    )

    plt.close()


# ============================================================
# PLOT 3
# DEATH AGE - HARSH ONLY
# ============================================================

def plot_death_age_harsh(
    death_data,
    environment_name,
):

    if death_data.empty:
        return

    data = death_data[
        death_data["Environment"] == environment_name
    ].copy()

    if data.empty:
        return

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # We do NOT pool the 10 replicates as raw counts.
    #
    # Each replicate starts with 50 agents per strategy.
    # Therefore deaths are converted to percentages within
    # each replicate before averaging.
    # --------------------------------------------------------

    age_counts = (
        data
        .groupby(
            [
                "Replicate",
                "Age",
                "Strategy",
            ],
            as_index=False,
        )
        .size()
        .rename(
            columns={"size": "Deaths"}
        )
    )

    age_counts["DeathPct"] = (
        age_counts["Deaths"]
        / (N_AGENTS / 2)
        * 100
    )

    plot_data = (
        age_counts
        .groupby(
            [
                "Age",
                "Strategy",
            ],
            as_index=False,
        )
        .agg(
            MeanDeathPct=(
                "DeathPct",
                "mean",
            )
        )
    )

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )

    for strategy in ["patient", "impulsive"]:

        strategy_data = plot_data[
            plot_data["Strategy"] == strategy
        ]

        if strategy_data.empty:
            continue

        ax.plot(
            strategy_data["Age"],
            strategy_data["MeanDeathPct"],
            marker="o",
            label=strategy.capitalize(),
        )

    ax.set_title(
        f"Death age distribution - {environment_name}"
    )

    ax.set_xlabel("Age at death")
    ax.set_ylabel(
        "Mean deaths per replicate (% of strategy)"
    )

    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()

    filename = (
        "death_age_"
        + safe_filename(environment_name)
        + ".png"
    )

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            filename,
        ),
        dpi=300,
    )

    plt.close()


# ============================================================
# PLOT 4
# DEATH AGE + ENERGY - HARSH ONLY
# ============================================================

def plot_death_age_energy_harsh(
    death_data,
    environment_name,
):

    if death_data.empty:
        return

    data = death_data[
        death_data["Environment"] == environment_name
    ].copy()

    if data.empty:
        return

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )

    for strategy in ["patient", "impulsive"]:

        strategy_data = data[
            data["Strategy"] == strategy
        ]

        if strategy_data.empty:
            continue

        ax.scatter(
            strategy_data["Age"],
            strategy_data["Energy"],
            alpha=0.35,
            label=strategy.capitalize(),
        )

    ax.set_title(
        f"Death age and energy - {environment_name}"
    )

    ax.set_xlabel("Age at death")
    ax.set_ylabel("Energy at death")

    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()

    filename = (
        "death_age_energy_"
        + safe_filename(environment_name)
        + ".png"
    )

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            filename,
        ),
        dpi=300,
    )

    plt.close()


# ============================================================
# OPTIONAL POPULATION GRAPH
# ============================================================

def plot_population(
    model_data,
    environment_name,
):

    data = model_data[
        model_data["Environment"] == environment_name
    ].copy()

    if data.empty:
        return

    # Average across replicates rather than pooling all agents.
    grouped = (
        data
        .groupby(
            [
                "Step",
                "Age",
            ],
            as_index=False,
        )
        .agg(
            Population=("Population", "mean"),
            PatientPopulation=(
                "Patient Population",
                "mean",
            ),
            ImpulsivePopulation=(
                "Impulsive Population",
                "mean",
            ),
        )
    )

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )

    ax.plot(
        grouped["Age"],
        grouped["Population"],
        label="Total",
    )

    ax.plot(
        grouped["Age"],
        grouped["PatientPopulation"],
        label="Patient",
    )

    ax.plot(
        grouped["Age"],
        grouped["ImpulsivePopulation"],
        label="Impulsive",
    )

    ax.set_title(
        f"Population - {environment_name}"
    )

    ax.set_xlabel("Age")
    ax.set_ylabel("Mean number of alive agents")

    ax.set_xlim(
        INITIAL_AGE,
        INITIAL_AGE + N_STEPS,
    )

    # This is deliberately kept at 100:
    # every replicate starts with exactly 100 agents.
    ax.set_ylim(
        0,
        N_AGENTS,
    )

    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()

    filename = (
        "population_"
        + safe_filename(environment_name)
        + ".png"
    )

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            filename,
        ),
        dpi=300,
    )

    plt.close()


# ============================================================
# GENERATE PLOTS
# ============================================================

def generate_plots(
    model_data,
    agent_data,
    death_data,
):

    ensure_output_directory()

    for environment_name in SCENARIOS.keys():

        environment = create_environment(
            environment_name
        )

        # ----------------------------------------------------
        # Survival graph
        # ----------------------------------------------------

        plot_survival_percentage(
            agent_data,
            environment_name,
        )

        # ----------------------------------------------------
        # Mean energy graph
        # ----------------------------------------------------

        plot_mean_energy(
            agent_data,
            environment_name,
        )

        # ----------------------------------------------------
        # Population graph
        # ----------------------------------------------------

        plot_population(
            model_data,
            environment_name,
        )

        # ----------------------------------------------------
        # Death-related graphs:
        #
        # ONLY HARSH
        # ----------------------------------------------------

        if environment.scenario_type == "Harsh":

            plot_death_age_harsh(
                death_data,
                environment_name,
            )

            plot_death_age_energy_harsh(
                death_data,
                environment_name,
            )


# ============================================================
# PRINT MAIN TABLE
# ============================================================

def print_main_results(
    survival_summary,
    energy_summary,
):

    print("\n" + "=" * 90)
    print("DESCRIPTIVE SURVIVAL RESULTS")
    print("=" * 90)

    columns = [
        "Environment",
        "Strategy",
        "MeanSurvivalPct",
        "SDSurvivalPct",
        "MinSurvivalPct",
        "MaxSurvivalPct",
    ]

    display_data = survival_summary[
        columns
    ].copy()

    for column in [
        "MeanSurvivalPct",
        "SDSurvivalPct",
        "MinSurvivalPct",
        "MaxSurvivalPct",
    ]:

        display_data[column] = (
            display_data[column]
            .round(2)
        )

    print(
        display_data.to_string(
            index=False
        )
    )

    print("\n" + "=" * 90)
    print("DESCRIPTIVE FINAL ENERGY RESULTS")
    print("=" * 90)

    if not energy_summary.empty:

        energy_display = energy_summary[
            [
                "Environment",
                "Strategy",
                "MeanFinalEnergy",
                "SDFinalEnergy",
            ]
        ].copy()

        energy_display[
            "MeanFinalEnergy"
        ] = (
            energy_display[
                "MeanFinalEnergy"
            ].round(2)
        )

        energy_display[
            "SDFinalEnergy"
        ] = (
            energy_display[
                "SDFinalEnergy"
            ].round(2)
        )

        print(
            energy_display.to_string(
                index=False
            )
        )


# ============================================================
# MAIN
# ============================================================

def main():

    ensure_output_directory()

    print("\n" + "=" * 90)
    print("DELAY DISCOUNTING SIMULATION")
    print("=" * 90)

    print(
        f"\nAgents per replicate: {N_AGENTS}"
    )

    print(
        f"Replicates per scenario: {N_REPLICATES}"
    )

    print(
        "\nEach replicate contains exactly:"
    )

    print(
        "  50 patient agents"
    )

    print(
        "  50 impulsive agents"
    )

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    (
        model_data,
        agent_data,
        death_data,
    ) = run_all_simulations()

    # --------------------------------------------------------
    # TABLES
    # --------------------------------------------------------

    (
        survival,
        survival_summary,
    ) = create_survival_tables(
        agent_data
    )

    energy_summary = create_energy_summary(
        agent_data
    )

    death_summary = create_death_summary(
        death_data
    )

    scenario_summary = create_scenario_summary(
        survival_summary,
        energy_summary,
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    save_tables(
        model_data,
        agent_data,
        death_data,
        survival,
        survival_summary,
        energy_summary,
        death_summary,
        scenario_summary,
    )

    # --------------------------------------------------------
    # PLOTS
    # --------------------------------------------------------

    generate_plots(
        model_data,
        agent_data,
        death_data,
    )

    # --------------------------------------------------------
    # PRINT
    # --------------------------------------------------------

    print_main_results(
        survival_summary,
        energy_summary,
    )

    print("\n" + "=" * 90)
    print("ANALYSIS COMPLETED")
    print("=" * 90)

    print(
        f"\nResults saved in: {OUTPUT_DIR}/"
    )


if __name__ == "__main__":
    main()