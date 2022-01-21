from solsim.base import BaseSystem


class LotkaVolterraSystem(BaseSystem):

  @property
  def quantities(self):
    return {
      'population_size',
      'food_supply'
    }

  def step(self):
    return {'population_size': 1, 'food_supply': 1}