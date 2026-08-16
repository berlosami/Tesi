# server.py

import sys

from mesa.visualization.ModularVisualization import (
    ModularServer,
)

from mesa.visualization.modules import (
    CanvasGrid,
    ChartModule,
)

from model import DelayDiscountingModel
from environments import create_environment


# ============================================================
# SCELTA AMBIENTE
# ============================================================

def choose_environment():

    if len(sys.argv) > 1:

        choice = sys.argv[1]

    else:

        print()
        print("=" * 50)
        print("SELEZIONE AMBIENTE")
        print("=" * 50)
        print()
        print("1 - Stable")
        print("2 - Volatile")
        print("3 - Harsh")
        print()

        choice = input(
            "Seleziona ambiente: "
        ).strip()

    return create_environment(
        choice
    )


environment = choose_environment()


# ============================================================
# VISUALIZZAZIONE AGENTE
# ============================================================

def agent_portrayal(agent):

    # Morto
    if not agent.alive:

        return {
            "Shape": "circle",
            "Color": "black",
            "Filled": True,
            "Layer": 0,
            "r": 0.30,
        }

    # Rosso = impulsivo
    if agent.is_impulsive:

        return {
            "Shape": "circle",
            "Color": "red",
            "Filled": True,
            "Layer": 1,
            "r": 0.45,
        }

    # Giallo = intermedio
    if agent.is_intermediate:

        return {
            "Shape": "circle",
            "Color": "yellow",
            "Filled": True,
            "Layer": 1,
            "r": 0.45,
        }

    # Verde = paziente
    return {
        "Shape": "circle",
        "Color": "green",
        "Filled": True,
        "Layer": 1,
        "r": 0.45,
    }


# ============================================================
# GRID
# ============================================================

canvas = CanvasGrid(
    agent_portrayal,
    20,
    20,
    500,
    500,
)


# ============================================================
# GRAFICO
# ============================================================

chart = ChartModule(
    [
        {
            "Label": "Population",
            "Color": "black",
        },
        {
            "Label": "Mean Energy",
            "Color": "blue",
        },
    ],
    data_collector_name="datacollector",
)


# ============================================================
# MODEL FACTORY
# ============================================================

def model_factory():

    return DelayDiscountingModel(
        environment=environment,
        width=20,
        height=20,
        n_agents=100,
    )


# ============================================================
# SERVER
# ============================================================

server = ModularServer(
    model_factory,
    [
        canvas,
        chart,
    ],
    f"Delay Discounting - {environment.NAME}",
    {},
)

server.port = 8521


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("MESA SERVER")
    print("=" * 60)
    print(
        f"Ambiente: {environment.NAME}"
    )
    print()
    print("Parametri:")
    print("  Agenti:           100")
    print("  Età iniziale:     10")
    print("  Energia iniziale: 8")
    print("  Costo metabolico: 1")
    print("  λ:                0.05 - 0.50")
    print("  R1:               2")
    print("  R2:               20")
    print("  D2:               7")
    print()

    if environment.VOLATILITY:

        print(
            "  R2 volatile:      sì"
        )

        print(
            "  P(R2):            0.50"
        )

        print(
            "  Evento:           indipendente per agente"
        )

    else:

        print(
            "  R2 volatile:      no"
        )

    print()

    if environment.AGE_MORTALITY:

        print(
            "  Mortalità age:    sì"
        )

    else:

        print(
            "  Mortalità age:    no"
        )

    print()
    print(
        "Server: http://127.0.0.1:8521"
    )
    print("=" * 60)
    print()

    server.launch()