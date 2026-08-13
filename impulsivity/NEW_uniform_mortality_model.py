from NEW_baseline_model import BaselineModel

class UniformMortalityModel(BaselineModel):
    MU_BASE = 0.04699

    def __init__(self, mortality_scale=1.0, seed=None):
        self.mortality_scale = float(mortality_scale)
        super().__init__(seed=seed)

    def get_mortality_probability(self, age):
        return min(self.MU_BASE * self.mortality_scale, 1.0)
