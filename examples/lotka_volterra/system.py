from solsim.base import BaseSystem


class LotkaVolterraSystem(BaseSystem):

  def __init__(
    self,
    population_size,
    food_supply
  ):
    self.population_size = population_size
    self.food_supply = food_supply

  def step(self):
    return {
      'population_size': self.population_size,
      'food_supply': self.food_supply
    }