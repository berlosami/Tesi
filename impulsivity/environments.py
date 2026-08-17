# environments.py

import random


class BaseEnvironment:
    """
    Parametri comuni a tutti gli ambienti.

    R1 = 2
    R2 = 20
    D2 = 7
    costo metabolico = 1

    La differenza tra gli ambienti riguarda una sola condizione
    sperimentale alla volta:
        Stable   -> nessuna mortalità age-dependent
        Volatile -> volatilità di R2
        Harsh    -> mortalità age-dependent
    """

    NAME = "Base"

    R1 = 2.0
    R2 = 20.0

    D1 = 0
    D2 = 7

    METABOLIC_COST = 1.0

    P_R2_SUCCESS = 0.50

    AGE_MORTALITY = False
    VOLATILITY = False

    def reward(self, choice):

        if choice == 1:
            return self.R1

        if choice == 2:
            return self.R2

        return 0.0

    def reward_available(self, choice, rng=None):

        # R1 è sempre disponibile
        if choice == 1:
            return True

        # R2
        if choice == 2:

            # Negli ambienti non volatili R2 è deterministica
            if not self.VOLATILITY:
                return True

            if rng is None:
                rng = random

            # Ogni agente ha il proprio evento casuale.
            # Non è un evento globale.
            return rng.random() < self.P_R2_SUCCESS

        return False


class StableEnvironment(BaseEnvironment):

    NAME = "Stable"

    # Controllo:
    # nessuna mortalità age-dependent
    AGE_MORTALITY = False

    # Nessuna volatilità
    VOLATILITY = False


class VolatileEnvironment(BaseEnvironment):

    NAME = "Volatile"

    # La volatilità è l'unica condizione aggiunta.
    VOLATILITY = True

    # R2 ha P = 0.50 per ogni singolo tentativo.
    P_R2_SUCCESS = 0.50

    # No mortalità age-dependent per questo ambiente.
    AGE_MORTALITY = False


class HarshEnvironment(BaseEnvironment):

    NAME = "Harsh"

    # Nessuna volatilità.
    VOLATILITY = False

    # Mortalità age-dependent.
    AGE_MORTALITY = True

    METABOLIC_COST = 2


def create_environment(choice):
    """
    Crea l'ambiente richiesto.

    Accetta:
        1 oppure "Stable"
        2 oppure "Volatile"
        3 oppure "Harsh"
    """

    if isinstance(choice, str):
        choice = choice.strip().lower()

        if choice in ("1", "stable"):
            return StableEnvironment()

        elif choice in ("2", "volatile"):
            return VolatileEnvironment()

        elif choice in ("3", "harsh"):
            return HarshEnvironment()

        else:
            raise ValueError(
                "Ambiente non valido. Usa 1 = Stable, "
                "2 = Volatile, 3 = Harsh."
            )

    if choice == 1:
        return StableEnvironment()

    elif choice == 2:
        return VolatileEnvironment()

    elif choice == 3:
        return HarshEnvironment()

    raise ValueError(
        "Ambiente non valido. Usa 1 = Stable, "
        "2 = Volatile, 3 = Harsh."
    )


def get_environment(choice):
    """
    Compatibilità con il resto del progetto.
    """
    return create_environment(choice)