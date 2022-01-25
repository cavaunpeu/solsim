from .system import LotkaVolterraSystem
from solsim.simulation import Simulation


def main():
  simulation = Simulation(
    system=LotkaVolterraSystem(
      population_size=50,
      food_supply=1000,
      reproduction_rate=.01,
      consumption_rate=.1,
    ),
    watchlist=(
      'population_size',
      'food_supply'
    ),
    n_steps=5
  )
  results = simulation.run()


if __name__ == '__main__':
  main()