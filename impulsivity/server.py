from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from environments import create_environment, get_scenario_names
from model import DelayDiscountingModel
from typing import Any

# ============================================================
# GLOBAL SCENARIO
# ============================================================

SELECTED_SCENARIO = None


# ============================================================
# AGENT PORTRAYAL
# ============================================================

def agent_portrayal(agent:Any) -> dict[str, Any]:

    if not agent.alive:
        return {
            "Shape": "circle",
            "Color": "white",
            "Filled": False,
            "Layer": 0,
            "r": 0.2,
        }

    if agent.strategy == "patient":
        return {
            "Shape": "circle",
            "Color": "blue",
            "Filled": True,
            "Layer": 1,
            "r": 0.5,
        }

    return {
        "Shape": "circle",
        "Color": "red",
        "Filled": True,
        "Layer": 1,
        "r": 0.5,
    }


# ============================================================
# MODEL FACTORY
# ============================================================

def model_factory():

    environment = create_environment(
        SELECTED_SCENARIO
    )

    return DelayDiscountingModel(
        environment=environment,
        n_agents=100,
    )


# ============================================================
# SCENARIO SELECTION
# ============================================================

def select_scenario():

    scenario_names = get_scenario_names()

    print("\n" + "=" * 70)
    print("AVAILABLE SCENARIOS")
    print("=" * 70)

    for index, scenario_name in enumerate(
        scenario_names,
        start=1,
    ):

        environment = create_environment(
            scenario_name
        )

        print(
            f"{index:2d}. "
            f"{scenario_name:<30} "
            f"| R2={environment.R2:<4.0f} "
            f"| cutoff={environment.lambda_cutoff:.5f}"
        )

    print("=" * 70)

    while True:

        choice = input(
            "\nSelect scenario number: "
        ).strip()

        try:

            choice = int(choice)

            if 1 <= choice <= len(scenario_names):
                return scenario_names[choice - 1]

            print(
                f"Please enter a number between "
                f"1 and {len(scenario_names)}."
            )

        except ValueError:

            print("Please enter a valid number.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    SELECTED_SCENARIO = select_scenario()

    environment = create_environment(
        SELECTED_SCENARIO
    )

    print("\n" + "=" * 70)
    print("SELECTED SCENARIO")
    print("=" * 70)

    print(
        environment.description()
    )

    print("=" * 70)

    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------

    grid = CanvasGrid(
        portrayal_method=agent_portrayal,
        grid_width=20,
        grid_height=20,
        canvas_width=600,
        canvas_height=600,
    )

    # --------------------------------------------------------
    # POPULATION CHART
    # --------------------------------------------------------

    population_chart = ChartModule(
        [
            {
                "Label": "Population",
                "Color": "black",
            },
            {
                "Label": "Patient Population",
                "Color": "blue",
            },
            {
                "Label": "Impulsive Population",
                "Color": "red",
            },
        ],
        data_collector_name="datacollector",
    )

    # --------------------------------------------------------
    # ENERGY CHART
    # --------------------------------------------------------

    energy_chart = ChartModule(
        [
            {
                "Label": "Mean Energy",
                "Color": "black",
            },
            {
                "Label": "Patient Mean Energy",
                "Color": "blue",
            },
            {
                "Label": "Impulsive Mean Energy",
                "Color": "red",
            },
        ],
        data_collector_name="datacollector",
    )

    # --------------------------------------------------------
    # SERVER
    # --------------------------------------------------------

    server = ModularServer(
        model_factory,
        [
            grid,
            population_chart,
            energy_chart,
        ],
        "Delay Discounting Simulation",
        {},
    )

    server.port = 8521

    print("\nServer starting...")
    print("Open: http://127.0.0.1:8521")

    server.launch()