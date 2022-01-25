from typing import Dict
from solsim.base import BaseSystem


class LotkaVolterraSystem(BaseSystem):
    def __init__(
        self,
        population_size,
        food_supply,
        reproduction_rate,
        consumption_rate,
    ):
        self.population_size = population_size
        self.food_supply = food_supply
        self.reproduction_rate = reproduction_rate
        self.consumption_rate = consumption_rate

    def initialStep(self) -> Dict:
        return {
            "population_size": self.population_size,
            "food_supply": self.food_supply,
        }

    def step(self, state, history) -> Dict:
        population_size = max(
            state["population_size"] + self.reproduction_rate * state["food_supply"], 0
        )
        food_supply = max(
            state["food_supply"] - self.consumption_rate * state["population_size"], 0
        )
        return {"population_size": population_size, "food_supply": food_supply}
