from NEW_baseline_model import BaselineModel

class AgeDependentMortalityModel(BaselineModel):
    AGE_MORTALITY = {
        "10_19": 0.01136,
        "20_39": 0.01247,
        "40_59": 0.01953,
        "60_79": 0.05795,
        "80_119": 0.05795,
    }

    def get_mortality_probability(self, age):
        if 10 <= age <= 19:
            return self.AGE_MORTALITY["10_19"]
        if 20 <= age <= 39:
            return self.AGE_MORTALITY["20_39"]
        if 40 <= age <= 59:
            return self.AGE_MORTALITY["40_59"]
        if 60 <= age <= 79:
            return self.AGE_MORTALITY["60_79"]
        if 80 <= age <= 119:
            return self.AGE_MORTALITY["80_119"]
        return 0.0
