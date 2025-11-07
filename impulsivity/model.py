import math

from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.space import MultiGrid

from environments import (
    LAMBDA_MIN,
    LAMBDA_MAX,
    create_environment,
)


# ============================================================
# MODEL PARAMETERS
# ============================================================

N_AGENTS = 100
GRID_WIDTH = 20
GRID_HEIGHT = 20

INITIAL_AGE = 10
INITIAL_ENERGY = 8

N_STEPS = 110


# ============================================================
# AGE MORTALITY
# ============================================================

AGE_MORTALITY_PROBABILITIES = {
    (0, 9): 0.04929,
    (10, 19): 0.01346,
    (20, 39): 0.01507,
    (40, 59): 0.02490,
    (60, 79): 0.07803,
    (80, 119): 0.07803,
}


def get_age_mortality_probability(age):
    for (min_age, max_age), probability in AGE_MORTALITY_PROBABILITIES.items():
        if min_age <= age <= max_age:
            return probability

    return 0.0


# ============================================================
# LAMBDA FUNCTIONS
# ============================================================

def generate_balanced_lambdas(rng, cutoff, n_agents):
    """
    Generate exactly 50 patient and 50 impulsive agents
    for a population of 100.

    Patient:
        lambda < cutoff

    Impulsive:
        lambda >= cutoff
    """

    if n_agents % 2 != 0:
        raise ValueError("N_AGENTS must be even to create an exact 50/50 split.")

    if not (LAMBDA_MIN < cutoff < LAMBDA_MAX):
        raise ValueError(
            f"Lambda cutoff {cutoff} is outside the allowed "
            f"range ({LAMBDA_MIN}, {LAMBDA_MAX})."
        )

    half = n_agents // 2

    patient_lambdas = [
        LAMBDA_MIN + rng.random() * (cutoff - LAMBDA_MIN)
        for _ in range(half)
    ]

    impulsive_lambdas = [
        cutoff + rng.random() * (LAMBDA_MAX - cutoff)
        for _ in range(half)
    ]

    lambdas = patient_lambdas + impulsive_lambdas

    rng.shuffle(lambdas)

    return lambdas


def lambda_category(lambda_value, cutoff):
    """
    Classify an agent according to the scenario-specific cutoff.
    """

    if lambda_value < cutoff:
        return "patient"

    return "impulsive"


def subjective_value(reward, delay, lambda_value):
    """
    Subjective value:

        V = R * exp(-lambda * delay)
    """

    return reward * math.exp(-lambda_value * delay)


# ============================================================
# AGENT
# ============================================================

class DelayDiscountingAgent(Agent):

    def __init__(self, unique_id, model, lambda_value):
        super().__init__(unique_id, model)

        self.age = INITIAL_AGE
        self.energy = INITIAL_ENERGY

        self.lambda_value = lambda_value

        self.strategy = lambda_category(
            self.lambda_value,
            self.model.environment.lambda_cutoff,
        )

        self.choice = None

        self.alive = True

    # --------------------------------------------------------
    # DECISION
    # --------------------------------------------------------

    def make_choice(self):
        value_1 = subjective_value(
            self.model.environment.R1,
            self.model.environment.D1,
            self.lambda_value,
        )

        value_2 = subjective_value(
            self.model.environment.R2,
            self.model.environment.D2,
            self.lambda_value,
        )

        if value_1 >= value_2:
            self.choice = 1
        else:
            self.choice = 2

    # --------------------------------------------------------
    # DEATH
    # --------------------------------------------------------

    def die(self, cause):
        if not self.alive:
            return

        self.alive = False

        self.model.death_records.append({
            "AgentID": self.unique_id,
            "Step": self.model.schedule.steps,
            "Age": self.age,
            "Lambda": self.lambda_value,
            "Strategy": self.strategy,
            "Energy": self.energy,
            "DeathCause": cause,
            "Environment": self.model.environment.name,
            "ScenarioType": self.model.environment.scenario_type,
            "R2": self.model.environment.R2,
            "LambdaCutoff": self.model.environment.lambda_cutoff,
            "MetabolicCost": self.model.environment.metabolic_cost,
            "P_R2_Success": self.model.environment.p_r2_success,
        })

    # --------------------------------------------------------
    # STEP
    # --------------------------------------------------------

    def step(self):

        if not self.alive:
            return

        current_step = self.model.schedule.steps + 1

        # Movimento casuale nella griglia
        possible_moves = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )

        new_position = self.random.choice(possible_moves)
        self.model.grid.move_agent(self, new_position)
        # ----------------------------------------------------
        # METABOLIC COST
        # ----------------------------------------------------

        self.energy -= self.model.environment.metabolic_cost

        if self.energy <= 0:
            self.die("Energy")
            return

        # ----------------------------------------------------
        # AGE-DEPENDENT MORTALITY
        # ----------------------------------------------------

        if self.model.environment.age_mortality:

            probability = get_age_mortality_probability(self.age)

            if self.random.random() < probability:
                self.die("Age")
                return

        # ----------------------------------------------------
        # DECISION
        # ----------------------------------------------------

        # New decision at the beginning of each 7-step cycle.
        if (current_step - 1) % self.model.environment.D2 == 0:
            self.make_choice()

        # ----------------------------------------------------
        # REWARD
        # ----------------------------------------------------

        if self.choice == 1:

            self.energy += self.model.environment.R1

        elif self.choice == 2:

            if current_step % self.model.environment.D2 == 0:

                if self.model.environment.reward_available(self.model):

                    self.energy += self.model.environment.R2

        # ----------------------------------------------------
        # AGE
        # ----------------------------------------------------

        self.age += 1


# ============================================================
# MODEL
# ============================================================

class DelayDiscountingModel(Model):

    def __init__(
        self,
        environment,
        n_agents=N_AGENTS,
        seed=None,
    ):

        super().__init__(seed=seed)

        self.environment = environment

        self.n_agents = n_agents

        self.death_records = []

        self.schedule = RandomActivation(self)

        self.grid = MultiGrid(GRID_WIDTH, GRID_HEIGHT, torus=True)

        # ----------------------------------------------------
        # EXACTLY 50 PATIENT + 50 IMPULSIVE
        # ----------------------------------------------------

        lambdas = generate_balanced_lambdas(
            self.random,
            self.environment.lambda_cutoff,
            self.n_agents,
        )

        for agent_id, lambda_value in enumerate(lambdas):

            agent = DelayDiscountingAgent(
                unique_id=agent_id,
                model=self,
                lambda_value=lambda_value,
            )

            self.schedule.add(agent)

            x = self.random.randrange(GRID_WIDTH)
            y = self.random.randrange(GRID_HEIGHT)
            self.grid.place_agent(agent, (x, y))

        # ----------------------------------------------------
        # DATA COLLECTOR
        # ----------------------------------------------------

        self.datacollector = DataCollector(

            model_reporters={

                "Population": lambda model: sum(
                    1
                    for agent in model.schedule.agents
                    if agent.alive
                ),

                "Mean Energy": lambda model: (
                    sum(
                        agent.energy
                        for agent in model.schedule.agents
                        if agent.alive
                    )
                    /
                    max(
                        1,
                        sum(
                            1
                            for agent in model.schedule.agents
                            if agent.alive
                        )
                    )
                ),

                "Patient Population": lambda model: sum(
                    1
                    for agent in model.schedule.agents
                    if agent.alive
                    and agent.strategy == "patient"
                ),

                "Impulsive Population": lambda model: sum(
                    1
                    for agent in model.schedule.agents
                    if agent.alive
                    and agent.strategy == "impulsive"
                ),

                "Patient Mean Energy": lambda model: (
                    sum(
                        agent.energy
                        for agent in model.schedule.agents
                        if agent.alive
                        and agent.strategy == "patient"
                    )
                    /
                    max(
                        1,
                        sum(
                            1
                            for agent in model.schedule.agents
                            if agent.alive
                            and agent.strategy == "patient"
                        )
                    )
                ),

                "Impulsive Mean Energy": lambda model: (
                    sum(
                        agent.energy
                        for agent in model.schedule.agents
                        if agent.alive
                        and agent.strategy == "impulsive"
                    )
                    /
                    max(
                        1,
                        sum(
                            1
                            for agent in model.schedule.agents
                            if agent.alive
                            and agent.strategy == "impulsive"
                        )
                    )
                ),

                "Mean Lambda": lambda model: (
                    sum(
                        agent.lambda_value
                        for agent in model.schedule.agents
                    )
                    / len(model.schedule.agents)
                ),

                "Lambda Variance": lambda model: (
                    sum(
                        (
                            agent.lambda_value
                            -
                            sum(
                                a.lambda_value
                                for a in model.schedule.agents
                            )
                            / len(model.schedule.agents)
                        ) ** 2
                        for agent in model.schedule.agents
                    )
                    / len(model.schedule.agents)
                ),
            },

            agent_reporters={

                "Age": "age",
                "Energy": "energy",
                "Lambda": "lambda_value",
                "Strategy": "strategy",
                "Alive": "alive",
            },
        )

        # Initial state: Step 0 / Age 10
        self.datacollector.collect(self)

    # --------------------------------------------------------
    # MODEL STEP
    # --------------------------------------------------------

    def step(self):

        self.schedule.step()

        self.datacollector.collect(self)

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run_model(self, steps=N_STEPS):

        for _ in range(steps):
            self.step()