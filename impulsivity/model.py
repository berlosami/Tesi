import math

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from environments import (
    StableEnvironment,
    VolatileEnvironment,
    HarshEnvironment,
)


# ============================================================
# PARAMETRI
# ============================================================

N_AGENTS = 100

GRID_WIDTH = 20
GRID_HEIGHT = 20

INITIAL_AGE = 10
INITIAL_ENERGY = 8.0

MAX_AGE = 120

LAMBDA_MIN = 0.05
LAMBDA_MAX = 0.50

R1 = 2.0
R2 = 20.0

D1 = 0
D2 = 7

METABOLIC_COST = 1.0

P_R2_SUCCESS = 0.50


# ============================================================
# MORTALITÀ AGE-DEPENDENT
# ============================================================

def age_mortality_probability(age):

    if 0 <= age <= 9:
        return 0.04699

    if 10 <= age <= 19:
        return 0.01136

    if 20 <= age <= 39:
        return 0.01247

    if 40 <= age <= 59:
        return 0.01953

    if 60 <= age <= 79:
        return 0.05795

    if 80 <= age <= 119:
        return 0.05795

    return 0.0


# ============================================================
# CLASSIFICAZIONE λ
# ============================================================

def lambda_category(lam):

    if lam is None:
        return "unknown"

    if not math.isfinite(lam):
        return "unknown"

    if lam < 0.20:
        return "patient"

    if lam < 0.35:
        return "intermediate"

    return "impulsive"


# ============================================================
# AGENTE
# ============================================================

class DelayDiscountingAgent(Agent):

    def __init__(self, unique_id, model):

        # Compatibile con Mesa 2.4.0
        super().__init__(unique_id, model)

        # ----------------------------------------------------
        # λ INDIVIDUALE E FISSO
        # ----------------------------------------------------

        self.lambda_value = self.random.uniform(
            LAMBDA_MIN,
            LAMBDA_MAX,
        )

        self.lambda_initial = self.lambda_value

        # ----------------------------------------------------
        # STATO
        # ----------------------------------------------------

        self.age = INITIAL_AGE
        self.energy = INITIAL_ENERGY
        self.alive = True

        # ----------------------------------------------------
        # MORTE
        # ----------------------------------------------------

        self.death_cause = None
        self.death_age = None
        self.death_energy = None

        # ----------------------------------------------------
        # DECISIONE
        # ----------------------------------------------------

        self.last_choice = None
        self.last_reward = 0.0

        # La scelta resta valida per il ciclo di 7 anni.
        self.current_choice = None

        # ----------------------------------------------------
        # INFORMAZIONI RICOMPENSA
        # ----------------------------------------------------

        self.last_reward_step = None

    # ========================================================
    # CATEGORIA
    # ========================================================

    @property
    def category(self):

        return lambda_category(
            self.lambda_value
        )

    @property
    def is_impulsive(self):

        return self.category == "impulsive"

    @property
    def is_intermediate(self):

        return self.category == "intermediate"

    @property
    def is_patient(self):

        return self.category == "patient"

    # ========================================================
    # UTILITÀ SOGGETTIVA
    # ========================================================

    def subjective_value(
        self,
        reward,
        delay,
    ):

        return reward * math.exp(
            -self.lambda_value * delay
        )

    # ========================================================
    # SCELTA
    # ========================================================

    def choose(self):

        value_1 = self.subjective_value(
            R1,
            D1,
        )

        value_2 = self.subjective_value(
            R2,
            D2,
        )

        if value_1 >= value_2:
            return 1

        return 2

    # ========================================================
    # MORTE
    # ========================================================

    def die(self, cause):

        if not self.alive:
            return

        self.alive = False

        self.death_cause = cause
        self.death_age = self.age
        self.death_energy = self.energy

        # ----------------------------------------------------
        # DEATH RECORD COMPLETO
        # ----------------------------------------------------

        self.model.death_records.append(
            {
                "AgentID": self.unique_id,
                "Step": self.model.current_step,
                "Age": self.age,
                "Lambda": self.lambda_value,
                "Strategy": self.category,
                "Energy": self.energy,
                "DeathCause": cause,
            }
        )

    # ========================================================
    # STEP
    # ========================================================

    def step(self):

        if not self.alive:
            return

        environment = self.model.environment

        current_step = self.model.current_step

        # ----------------------------------------------------
        # 1. COSTO METABOLICO
        # ----------------------------------------------------

        self.energy -= environment.METABOLIC_COST

        # Se energia <= 0 -> morte energetica
        if self.energy <= 0:

            self.die("energy")

            return

        # ----------------------------------------------------
        # 2. MORTALITÀ AGE-DEPENDENT
        # ----------------------------------------------------

        if environment.AGE_MORTALITY:

            mortality_probability = (
                age_mortality_probability(
                    self.age
                )
            )

            if self.random.random() < mortality_probability:

                self.die("age")

                return

        # ----------------------------------------------------
        # 3. DECISIONE
        #
        # La decisione viene presa all'inizio di ogni
        # nuovo ciclo di 7 anni:
        #
        # step 1  -> età 10
        # step 8  -> età 17
        # step 15 -> età 24
        # ...
        # ----------------------------------------------------

        cycle_start = (
            (current_step - 1) % D2 == 0
        )

        if cycle_start:

            self.current_choice = self.choose()

            self.last_choice = self.current_choice

        # ----------------------------------------------------
        # 4. RICOMPENSA
        # ----------------------------------------------------

        reward = 0.0

        # ----------------------------------------------------
        # CHOICE 1
        #
        # R1 = 2 ogni singolo step
        # ----------------------------------------------------

        if self.current_choice == 1:

            reward = R1

        # ----------------------------------------------------
        # CHOICE 2
        #
        # R2 = 20 solo dopo 7 step.
        #
        # Quindi:
        #
        # età 10 -> nessuna R2
        # età 17 -> R2
        # età 24 -> R2
        # età 31 -> R2
        # ...
        #
        # La volatilità viene applicata INDIVIDUALMENTE
        # al momento della ricompensa.
        # ----------------------------------------------------

        elif self.current_choice == 2:

            reward_due = (
                current_step % D2 == 0
            )

            if reward_due:

                reward_available = (
                    environment.reward_available(
                        2,
                        rng=self.random,
                    )
                )

                if reward_available:

                    reward = R2

                else:

                    reward = 0.0

        self.last_reward = reward
        self.last_reward_step = current_step

        # ----------------------------------------------------
        # 5. AGGIORNAMENTO ENERGIA
        # ----------------------------------------------------

        self.energy += reward

        # Non esiste E_MAX

        if self.energy <= 0:

            self.die("energy")

            return

        # ----------------------------------------------------
        # 6. MOVIMENTO
        # ----------------------------------------------------

        neighborhood = (
            self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False,
            )
        )

        if neighborhood:

            new_position = self.random.choice(
                neighborhood
            )

            self.model.grid.move_agent(
                self,
                new_position,
            )

        # ----------------------------------------------------
        # 7. INVECCHIAMENTO
        # ----------------------------------------------------

        self.age += 1


# ============================================================
# MODELLO
# ============================================================

class DelayDiscountingModel(Model):

    def __init__(
        self,
        environment,
        width=GRID_WIDTH,
        height=GRID_HEIGHT,
        n_agents=N_AGENTS,
        seed=None,
    ):

        super().__init__(seed=seed)

        self.environment = environment

        self.width = width
        self.height = height

        self.n_agents = n_agents

        # ----------------------------------------------------
        # STEP ESPLICITO
        # ----------------------------------------------------

        self.current_step = 0

        # ----------------------------------------------------
        # DEATH RECORDS
        # ----------------------------------------------------

        self.death_records = []

        # ----------------------------------------------------
        # GRIGLIA
        # ----------------------------------------------------

        self.grid = MultiGrid(
            width,
            height,
            torus=False,
        )

        # ----------------------------------------------------
        # SCHEDULER
        # ----------------------------------------------------

        self.schedule = RandomActivation(
            self
        )

        # ----------------------------------------------------
        # AGENTI
        # ----------------------------------------------------

        for i in range(n_agents):

            agent = DelayDiscountingAgent(
                i,
                self,
            )

            self.schedule.add(
                agent
            )

            x = self.random.randrange(
                width
            )

            y = self.random.randrange(
                height
            )

            self.grid.place_agent(
                agent,
                (x, y),
            )

        # ----------------------------------------------------
        # DATA COLLECTOR
        # ----------------------------------------------------

        self.datacollector = DataCollector(

            model_reporters={

                "Population":
                    self.population,

                "Mean Energy":
                    self.mean_energy,

                "Mean Lambda":
                    self.mean_lambda,

                "Lambda Variance":
                    self.lambda_variance,

                "Impulsive Fraction":
                    self.impulsive_fraction,

                "Intermediate Fraction":
                    self.intermediate_fraction,

                "Patient Fraction":
                    self.patient_fraction,

                "Energy Deaths":
                    self.energy_deaths,

                "Age Deaths":
                    self.age_deaths,
            },

            agent_reporters={

                "Age":
                    lambda a: a.age,

                "Energy":
                    lambda a: a.energy,

                "Lambda":
                    lambda a: a.lambda_value,

                "Category":
                    lambda a: a.category,

                "Alive":
                    lambda a: a.alive,

                "Death DeathCause":
                    lambda a: a.death_cause,

                "Death Age":
                    lambda a: a.death_age,

                "Death Energy":
                    lambda a: a.death_energy,

                "Choice":
                    lambda a: a.last_choice,

                "Reward":
                    lambda a: a.last_reward,
            },
        )

        # Stato iniziale
        self.datacollector.collect(
            self
        )

        self.running = True

    # ========================================================
    # AGENTI VIVI
    # ========================================================

    def alive_agents(self):

        return [
            agent
            for agent in self.schedule.agents
            if agent.alive
        ]

    # ========================================================
    # POPOLAZIONE
    # ========================================================

    def population(self):

        return len(
            self.alive_agents()
        )

    # ========================================================
    # ENERGIA MEDIA
    # ========================================================

    def mean_energy(self):

        agents = self.alive_agents()

        if not agents:
            return 0.0

        return sum(
            agent.energy
            for agent in agents
        ) / len(agents)

    # ========================================================
    # λ MEDIA
    # ========================================================

    def mean_lambda(self):

        agents = self.alive_agents()

        if not agents:
            return 0.0

        return sum(
            agent.lambda_value
            for agent in agents
        ) / len(agents)

    # ========================================================
    # VARIANZA λ
    # ========================================================

    def lambda_variance(self):

        agents = self.alive_agents()

        if len(agents) < 2:
            return 0.0

        values = [
            agent.lambda_value
            for agent in agents
        ]

        mean = sum(values) / len(values)

        return sum(
            (x - mean) ** 2
            for x in values
        ) / (len(values) - 1)

    # ========================================================
    # FRAZIONI
    # ========================================================

    def impulsive_fraction(self):

        agents = self.alive_agents()

        if not agents:
            return 0.0

        return sum(
            agent.is_impulsive
            for agent in agents
        ) / len(agents)

    def intermediate_fraction(self):

        agents = self.alive_agents()

        if not agents:
            return 0.0

        return sum(
            agent.is_intermediate
            for agent in agents
        ) / len(agents)

    def patient_fraction(self):

        agents = self.alive_agents()

        if not agents:
            return 0.0

        return sum(
            agent.is_patient
            for agent in agents
        ) / len(agents)

    # ========================================================
    # MORTI
    # ========================================================

    def energy_deaths(self):

        return sum(
            1
            for agent in self.schedule.agents
            if agent.death_cause == "energy"
        )

    def age_deaths(self):

        return sum(
            1
            for agent in self.schedule.agents
            if agent.death_cause == "age"
        )

    # ========================================================
    # STEP DEL MODELLO
    # ========================================================

    def step(self):

        self.current_step += 1

        self.schedule.step()

        self.datacollector.collect(
            self
        )

        # Il modello termina dopo 110 step:
        # 10 -> 120 anni.
        #
        # NON uccidiamo gli agenti a 120:
        # Stable deve rimanere privo di mortalità
        # age-dependent.

        if self.current_step >= 110:

            self.running = False
    