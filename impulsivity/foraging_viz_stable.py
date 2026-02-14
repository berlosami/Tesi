from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from foraging_model import ForagingModel
import math


def agent_portrayal(agent):
    if agent.last_choice == "risky":
        color = "blue"
    else:
        color = "red"

    return {
        "Shape": "circle",
        "Color": color,
        "Filled": "true",
        "Layer": 0,
        # FIX 2 — scala non lineare della dimensione
        "r": 0.3 + math.sqrt(agent.energy) * 0.05,
        "Text": str(agent.unique_id),
        "Text_color": "black"
    }


grid = CanvasGrid(agent_portrayal, 20, 20, 400, 400)

server = ModularServer(
    ForagingModel,
    [grid],
    "Ambiente stabile",
    {"n_agents": 25, "environment": "stable"}
)

server.port = 8521
server.launch()



