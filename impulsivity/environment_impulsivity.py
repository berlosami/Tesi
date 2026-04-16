import numpy as np

class BaseEnvironment:
    def __init__(self, model):
        self.model = model

    def get_reward(self, choice):
        return 0

class StableEnvironment(BaseEnvironment):
    def get_reward(self, choice):
        p = self.model.p
        return p['R1'] if choice == 1 else p['R2']

class VolatileEnvironment(BaseEnvironment):
    def get_reward(self, choice):
        p = self.model.p
        if choice == 1:
            return p['R1']
        if np.random.random() < p['P_R2_SUCCESS']:
            return p['R2']
        return 0

class HarshEnvironment(BaseEnvironment):
    def get_reward(self, choice):
        p = self.model.p
        return p['R1'] if choice == 1 else p['R2']