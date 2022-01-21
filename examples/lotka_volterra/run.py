import argparse
import pdb

from system import LotkaVolterraSystem
from solsim.simulation import Simulation


if __name__ == '__main__':
  simulation = Simulation(
    system=LotkaVolterraSystem(),
    watchlist=(
      'population_size',
      'food_supply'
    ),
    n_steps=1
  )
  results = simulation.run()
