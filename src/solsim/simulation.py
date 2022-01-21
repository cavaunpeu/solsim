from typing import Dict, Set

import pandas as pd


class Simulation:

  def __init__(self, system, watchlist, n_steps) -> None:
    self.system = system
    self.watchlist = watchlist
    self.n_steps = n_steps

  def run(self) -> pd.DataFrame:
    results = []
    for step in range(self.n_steps):
      res = self.system.step()
      res = self._trim_result(res, self.watchlist)
      res = {**res, 'step': step}
      results.append(res)
    return pd.DataFrame(results)

  @staticmethod
  def _trim_result(result: Dict, watchlist: Set) -> Dict:
    for quantity in watchlist:
      if quantity not in result:
        raise Exception(f'{quantity} not found in result: {result}')
    return {quantity: result[quantity] for quantity in watchlist}