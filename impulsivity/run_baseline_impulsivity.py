from mesa.space import MultiGrid
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from model_baseline_impulsivity import SurvivalModel, PARAMS


# Patch grafico al modello base
_original_init = SurvivalModel.__init__
_original_step = SurvivalModel.step


def patched_init(self, p):
    _original_init(self, p)

    # aggiunge spazio grafico
    self.grid = MultiGrid(20, 20, torus=True)

    # posiziona agenti casualmente
    for agent in self.schedule.agents:
        x = self.random.randrange(self.grid.width)
        y = self.random.randrange(self.grid.height)
        self.grid.place_agent(agent, (x, y))


def patched_step(self):
    # movimento grafico prima dello step reale
    for agent in self.schedule.agents:
        if agent.alive:
            possible_steps = self.grid.get_neighborhood(
                agent.pos,
                moore=True,
                include_center=False
            )

            new_position = self.random.choice(possible_steps)
            self.grid.move_agent(agent, new_position)

    _original_step(self)


# applica patch
SurvivalModel.__init__ = patched_init
SurvivalModel.step = patched_step


# Aspetto agenti
def agent_portrayal(agent):
    color = "blue" if agent.lam == PARAMS["LAMBDA_LOW"] else "red"

    if not agent.alive:
        color = "black"

    return {
        "Shape": "circle",
        "Color": color,
        "Filled": "true",
        "Layer": 0,
        "r": 0.6
    }


# Grafica
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

chart = ChartModule([
    {"Label": "Population", "Color": "Black"}
])


# Avvio server
server = ModularServer(
    SurvivalModel,
    [grid, chart],
    "Baseline Impulsivity Model",
    {"p": PARAMS}
)

server.port = 8521
server.launch()