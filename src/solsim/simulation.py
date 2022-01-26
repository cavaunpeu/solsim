import asyncio
from collections.abc import Iterable
from typing import Dict, List, Set, Union

import pandas as pd
from tqdm.auto import tqdm

from solsim.system import BaseSystem, BaseSolanaSystem
from solsim.type import StateType


class Simulation:
    def __init__(self, system: Union[BaseSystem, BaseSolanaSystem], watchlist: Iterable[str], n_steps: int) -> None:
        self._system = system
        self._watchlist = set(watchlist)
        self._n_steps = n_steps
        self._system_uses_solana = isinstance(self._system, BaseSolanaSystem)

    def run(self) -> pd.DataFrame:
        return asyncio.run(self._run())

    async def _run(self) -> pd.DataFrame:
        try:
            state: StateType = {}
            history: list[StateType] = []
            results: list[StateType] = []
            for step in tqdm(range(-1, self._n_steps - 1), desc="Steps completed"):
                if step == -1:
                    updates = (
                        await self._system.initialStep()
                        if self._system_uses_solana
                        else self._system.initialStep()
                    )
                else:
                    updates = (
                        await self._system.step(state, history)
                        if self._system_uses_solana
                        else self._system.step(state, history)
                    )
                state = {**state, **updates, "step": step}
                history.append(state)
                results.append(self._filter_state(state))
        finally:
            if self._system_uses_solana:
                await self._system.tearDown()
        return pd.DataFrame(results)

    def _filter_state(self, state: StateType) -> StateType:
        for qty in self._watchlist:
            if qty not in state:
                raise Exception(f"{qty} not found in state: {state}")
        return {qty: state[qty] for qty in self._watchlist | {"step"}}
