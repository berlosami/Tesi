from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from model_environment_impulsivity import SurvivalModel, PARAMS


choice = input(
    "Choose environment (stable / volatile / harsh): "
).strip().lower()

if choice not in ["stable", "volatile", "harsh"]:
    choice = "stable"

params = PARAMS.copy()
params["ENVIRONMENT"] = choice


def agent_portrayal(agent):

    if not agent.alive:
        color = "black"

    elif agent.lam < 0.20:
        color = "blue"

    elif agent.lam < 0.35:
        color = "purple"

    else:
        color = "red"

    return {
        "Shape": "circle",
        "Color": color,
        "Filled": "true",
        "Layer": 0,
        "r": 0.6
    }


grid = CanvasGrid(
    agent_portrayal,
    params["WIDTH"],
    params["HEIGHT"],
    500,
    500
)

chart = ChartModule([
    {"Label": "Population", "Color": "Black"},
    {"Label": "MeanLambdaAlive", "Color": "Blue"},
    {"Label": "MeanEnergyAlive", "Color": "Green"},
    {"Label": "VarLambdaAlive", "Color": "Orange"},
])


server = ModularServer(
    SurvivalModel,
    [grid, chart],
    f"Impulsivity Model - {choice.capitalize()}",
    {"p": params}
)

server.port = 8521
server.launch()