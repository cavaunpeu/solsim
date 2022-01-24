from typing import Dict, Set

import pandas as pd


class Simulation:

  def __init__(self, system, watchlist, n_steps) -> None:
    self._system = system
    self._watchlist = set(watchlist)
    self._n_steps = n_steps

  def run(self) -> pd.DataFrame:
    history, results = [], []
    for step in range(-1, self._n_steps):
      if step == -1:
        state = self._system.initialStep()
      else:
        state = self._system.step(state, history)
      state = {**state, 'step': step}
      history.append(state)
      results.append(self._filter_state(state))
    return pd.DataFrame(results)

  @staticmethod
  def _trim_result(result: Dict, watchlist: Set) -> Dict:
    for quantity in watchlist:
      if quantity not in result:
        raise Exception(f'{quantity} not found in result: {result}')
    return {quantity: result[quantity] for quantity in watchlist}