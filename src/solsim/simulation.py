import asyncio
from typing import Dict, Set

import pandas as pd
from tqdm.auto import tqdm


class Simulation:
    def __init__(self, system, watchlist, n_steps) -> None:
        self._system = system
        self._watchlist = set(watchlist)
        self._n_steps = n_steps

    def run(self) -> pd.DataFrame:
        return asyncio.run(self._run())

    async def _run(self) -> pd.DataFrame:
        try:
            state, history, results = {}, [], []
            for step in tqdm(range(-1, self._n_steps), desc="Steps completed"):
                if step == -1:
                    updates = (
                        await self._system.initialStep()
                        if self._system.uses_solana
                        else self._system.initialStep()
                    )
                else:
                    updates = (
                        await self._system.step(state, history)
                        if self._system.uses_solana
                        else self._system.step(state, history)
                    )
                state = {**state, **updates, "step": step}
                history.append(state)
                results.append(self._filter_state(state))
        finally:
            if self._system.uses_solana:
                await self._system.tearDown()
        return pd.DataFrame(results)

    def _filter_state(self, state: Dict) -> Dict:
        for qty in self._watchlist:
            if qty not in state:
                raise Exception(f"{qty} not found in state: {state}")
        return {qty: state[qty] for qty in self._watchlist | {"step"}}
