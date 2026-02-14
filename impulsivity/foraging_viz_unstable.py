from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from foraging_model import ForagingModel

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
        "r": 0.2 + agent.energy * 0.02,
        "Text": str(agent.unique_id),
        "Text_color": "black"
    }


grid = CanvasGrid(agent_portrayal, 20, 20, 400, 400)

server = ModularServer(
    ForagingModel,
    [grid],
    "Ambiente instabile",
    {"n_agents": 25, "environment": "unstable"}
)

server.port = 8522
server.launch()
