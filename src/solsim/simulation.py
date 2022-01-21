import pandas as pd


class Simulation:

  def __init__(self, system, watchlist, n_steps) -> None:
    watchlist = set(watchlist)
    quantities = system.quantities
    if not watchlist.issubset(quantities):
      invalid_quantities = {q for q in watchlist if q not in quantities}
      raise Exception(f"Please add {invalid_quantities} to quantities if you'd like to watch these quantities")

    self.system = system
    self.watchlist = watchlist
    self.n_steps = n_steps

  def run(self) -> pd.DataFrame:
    results = []
    for step in range(self.n_steps):
      res = {**self.system.step(), 'step': step}
      results.append(res)
    return pd.DataFrame(results)