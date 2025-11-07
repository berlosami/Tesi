import math
from typing import Any

# ============================================================
# GLOBAL PARAMETERS
# ============================================================

R1 = 2.0
D1 = 0
D2 = 7

LAMBDA_MIN = 0.05
LAMBDA_MAX = 0.50


# ============================================================
# SCENARIO CONFIGURATIONS
# ============================================================

SCENARIOS:dict[str, dict[str, Any]] = {
    # --------------------------------------------------------
    # STABLE
    # --------------------------------------------------------
    "Stable_R2_20": {
        "scenario_type": "Stable",
        "R1": R1,
        "R2": 20.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.0,
        "p_r2_success": 1.0,
        "volatility": False,
        "age_mortality": False,
    },

    # --------------------------------------------------------
    # VOLATILE - R2 = 20
    # --------------------------------------------------------
    "Volatile_R2_20_P0.75": {
        "scenario_type": "Volatile",
        "R1": R1,
        "R2": 20.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.0,
        "p_r2_success": 0.75,
        "volatility": True,
        "age_mortality": False,
    },

    "Volatile_R2_20_P0.50": {
        "scenario_type": "Volatile",
        "R1": R1,
        "R2": 20.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.0,
        "p_r2_success": 0.50,
        "volatility": True,
        "age_mortality": False,
    },

    "Volatile_R2_20_P0.25": {
        "scenario_type": "Volatile",
        "R1": R1,
        "R2": 20.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.0,
        "p_r2_success": 0.25,
        "volatility": True,
        "age_mortality": False,
    },

    # --------------------------------------------------------
    # VOLATILE - R2 = 40
    # --------------------------------------------------------
    "Volatile_R2_40_P0.75": {
        "scenario_type": "Volatile",
        "R1": R1,
        "R2": 40.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.0,
        "p_r2_success": 0.75,
        "volatility": True,
        "age_mortality": False,
    },

    "Volatile_R2_40_P0.50": {
        "scenario_type": "Volatile",
        "R1": R1,
        "R2": 40.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.0,
        "p_r2_success": 0.50,
        "volatility": True,
        "age_mortality": False,
    },

    "Volatile_R2_40_P0.25": {
        "scenario_type": "Volatile",
        "R1": R1,
        "R2": 40.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.0,
        "p_r2_success": 0.25,
        "volatility": True,
        "age_mortality": False,
    },

    # --------------------------------------------------------
    # HARSH - R2 = 20
    # --------------------------------------------------------
    "Harsh_R2_20_Cost1.2": {
        "scenario_type": "Harsh",
        "R1": R1,
        "R2": 20.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.2,
        "p_r2_success": 1.0,
        "volatility": False,
        "age_mortality": True,
    },

    "Harsh_R2_20_Cost1.4": {
        "scenario_type": "Harsh",
        "R1": R1,
        "R2": 20.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.4,
        "p_r2_success": 1.0,
        "volatility": False,
        "age_mortality": True,
    },

    "Harsh_R2_20_Cost1.6": {
        "scenario_type": "Harsh",
        "R1": R1,
        "R2": 20.0,
        "D1": D1,
        "D2": D2,
        "metabolic_cost": 1.6,
        "p_r2_success": 1.0,
        "volatility": False,
        "age_mortality": True,
    },
}


# ============================================================
# ENVIRONMENT CLASS
# ============================================================

class BaseEnvironment:
    """
    Parameterized environment.

    The environment stores only the parameters that differ
    between scenarios.
    """

    def __init__(
        self,
        name,
        scenario_type,
        R1,
        R2,
        D1,
        D2,
        metabolic_cost,
        p_r2_success,
        volatility,
        age_mortality,
    ):
        self.name = name
        self.scenario_type = scenario_type

        self.R1 = R1
        self.R2 = R2
        self.D1 = D1
        self.D2 = D2

        self.metabolic_cost = metabolic_cost
        self.p_r2_success = p_r2_success

        self.volatility = volatility
        self.age_mortality = age_mortality

    @property
    def lambda_cutoff(self):
        """
        Critical lambda separating patient and impulsive agents.

        lambda* = ln(R2/R1) / D2
        """
        return math.log(self.R2 / self.R1) / self.D2

    def reward_available(self, model):
        """
        Determines whether delayed reward R2 is available.

        In stable/harsh environments, R2 is always available.

        In volatile environments, R2 is available with probability
        p_r2_success.
        """
        if not self.volatility:
            return True

        return model.random.random() < self.p_r2_success

    def reward(self, choice):
        """
        Immediate reward for choice 1.
        Delayed reward amount for choice 2.
        """
        if choice == 1:
            return self.R1

        return self.R2

    def description(self):
        return (
            f"{self.name} | "
            f"type={self.scenario_type}, "
            f"R1={self.R1}, R2={self.R2}, "
            f"D2={self.D2}, "
            f"lambda*={self.lambda_cutoff:.5f}, "
            f"cost={self.metabolic_cost}, "
            f"P(R2)={self.p_r2_success}"
        )


# ============================================================
# ENVIRONMENT FACTORY
# ============================================================

def get_scenario_names():
    """Return scenario names in the defined order."""
    return list(SCENARIOS.keys())


def create_environment(choice):
    """
    Create an environment from:
    - scenario name
    - numeric index (1-based)
    """

    if isinstance(choice, int):
        scenario_names = get_scenario_names()

        if choice < 1 or choice > len(scenario_names):
            raise ValueError(
                f"Scenario index must be between 1 and {len(scenario_names)}."
            )

        choice = scenario_names[choice - 1]

    if not isinstance(choice, str):
        raise ValueError("Scenario must be a string or integer.")

    normalized = choice.strip().lower()

    selected_name = None

    for scenario_name in SCENARIOS:
        if normalized == scenario_name.lower():
            selected_name = scenario_name
            break

    if selected_name is None:
        raise ValueError(
            f"Unknown scenario '{choice}'. "
            f"Available scenarios: {', '.join(SCENARIOS.keys())}"
        )

    config = SCENARIOS[selected_name]

    return BaseEnvironment(
        name=selected_name,
        scenario_type=config["scenario_type"],
        R1=config["R1"],
        R2=config["R2"],
        D1=config["D1"],
        D2=config["D2"],
        metabolic_cost=config["metabolic_cost"],
        p_r2_success=config["p_r2_success"],
        volatility=config["volatility"],
        age_mortality=config["age_mortality"],
    )


# Backward-compatible function name
def get_environment(choice):
    return create_environment(choice)