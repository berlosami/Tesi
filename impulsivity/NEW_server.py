from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import Choice

from NEW_baseline_model import BaselineModel
from NEW_uniform_mortality_model import UniformMortalityModel
from NEW_age_dependent_model import AgeDependentMortalityModel


# ============================================================
# MODEL FACTORY
# ============================================================

def model_factory(model_type="Baseline", mortality_scale=0.0):

    if model_type == "Baseline":
        return BaselineModel()

    elif model_type == "Uniform mortality":
        return UniformMortalityModel(
            mortality_scale=mortality_scale
        )

    elif model_type == "Age-dependent mortality":
        return AgeDependentMortalityModel()

    else:
        return BaselineModel()


# ============================================================
# VISUALIZZAZIONE AGENTI
# ============================================================

def agent_portrayal(agent):

    if not agent.alive:
        return {
            "Shape": "circle",
            "Color": "black",
            "Filled": "true",
            "Layer": 0,
            "r": 0.3,
        }

    # --------------------------------------------------------
    # Strategia basata sulla soglia di delay discounting
    # --------------------------------------------------------

    strategy = agent.get_strategy()

    if strategy == "patient":

        color = "green"

    elif strategy == "impulsive":

        color = "red"

    else:

        color = "yellow"

    return {
        "Shape": "circle",
        "Color": color,
        "Filled": "true",
        "Layer": 1,
        "r": 0.7,
    }


# ============================================================
# CANVAS GRID
# ============================================================

GRID_WIDTH = 20
GRID_HEIGHT = 20

grid = CanvasGrid(
    agent_portrayal,
    GRID_WIDTH,
    GRID_HEIGHT,
    600,
    600,
)


# ============================================================
# CHART
# ============================================================

chart_population = ChartModule(
    [
        {
            "Label": "Population",
            "Color": "black",
        }
    ],
    data_collector_name="datacollector",
)


chart_energy = ChartModule(
    [
        {
            "Label": "Mean Energy",
            "Color": "blue",
        },
        {
            "Label": "Mean Energy Patient",
            "Color": "green",
        },
        {
            "Label": "Mean Energy Impulsive",
            "Color": "red",
        },
    ],
    data_collector_name="datacollector",
)


chart_lambda = ChartModule(
    [
        {
            "Label": "Mean Lambda x100",
            "Color": "purple",
        },
        {
            "Label": "Lambda Variance x1000",
            "Color": "orange",
        },
    ],
    data_collector_name="datacollector",
)


chart_strategy = ChartModule(
    [
        {
            "Label": "Patient Fraction",
            "Color": "green",
        },
        {
            "Label": "Impulsive Fraction",
            "Color": "red",
        },
    ],
    data_collector_name="datacollector",
)


# ============================================================
# PARAMETRI INTERATTIVI
# ============================================================

model_type = Choice(
    "Model type",
    value="Baseline",
    choices=[
        "Baseline",
        "Uniform mortality",
        "Age-dependent mortality",
    ],
)


mortality_scale = Choice(
    "Uniform mortality scale",
    value=0.0,
    choices=[
        0.0,
        0.1,
        0.2,
        0.3,
        0.5,
        0.7,
        1.0,
    ],
)


# ============================================================
# MODEL FUNCTION
# ============================================================

def model_factory_with_params(
    model_type,
    mortality_scale,
):

    if model_type == "Baseline":

        return BaselineModel()

    if model_type == "Uniform mortality":

        return UniformMortalityModel(
            mortality_scale=float(mortality_scale)
        )

    if model_type == "Age-dependent mortality":

        return AgeDependentMortalityModel()

    return BaselineModel()


# ============================================================
# SERVER
# ============================================================

server = ModularServer(
    model_factory_with_params,

    [
        grid,
        chart_population,
        chart_energy,
        chart_lambda,
        chart_strategy,
    ],

    "Impulsivity – Delay Discounting ABM",

    {
        "model_type": model_type,
        "mortality_scale": mortality_scale,
    },
)


server.port = 8521


if __name__ == "__main__":

    print()
    print("=" * 60)
    print(" IMPULSIVITY ABM – MESA SERVER")
    print("=" * 60)
    print()
    print("Apri nel browser:")
    print()
    print("http://127.0.0.1:8521")
    print()
    print("Premi Ctrl+C nel terminale per interrompere.")
    print()

    server.launch()