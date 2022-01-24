import asyncio
from typing import Dict, Set

import pandas as pd


class Simulation:

  def __init__(self, system, watchlist, n_steps) -> None:
    self._system = system
    self._watchlist = set(watchlist)
    self._n_steps = n_steps

  def run(self) -> pd.DataFrame:
    return asyncio.run(self._run())

  async def _run(self) -> pd.DataFrame:
    history, results = [], []
    for step in range(-1, self._n_steps):
      if step == -1:
        state = await self._system.initialStep() if self._system.uses_solana else self._system.initialStep()
      else:
        state = await self._system.step(state, history) if self._system.uses_solana else self._system.step(state, history)
      state = {**state, 'step': step}
      history.append(state)
      results.append(self._filter_state(state))
    if self._system.uses_solana:
      await self._system.tearDown()
    return pd.DataFrame(results)

  def _filter_state(self, result: Dict) -> Dict:
    for qty in self._watchlist:
      if qty not in result:
        raise Exception(f'{qty} not found in result: {result}')
    return {qty: result[qty] for qty in self._watchlist | {'step'}}