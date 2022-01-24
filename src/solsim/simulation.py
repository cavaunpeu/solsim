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

  def _filter_state(self, result: Dict) -> Dict:
    for qty in self._watchlist:
      if qty not in result:
        raise Exception(f'{qty} not found in result: {result}')
    return {qty: result[qty] for qty in self._watchlist | {'step'}}