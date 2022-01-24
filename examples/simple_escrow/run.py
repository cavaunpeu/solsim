import os

from system import SimpleEscrowSystem
from solsim.simulation import Simulation


if __name__ == '__main__':
  simulation = Simulation(
    system=SimpleEscrowSystem(
      workspace_dir=os.path.join(os.path.dirname(__file__), 'workspace')
    ),
    watchlist=(
      'foo_coin_trade_volume',
      'bar_coin_trade_volume'
    ),
    n_steps=5
  )
  results = simulation.run()