import asyncio
from collections.abc import Iterable
import os
import subprocess
import tempfile
from typing import Union

import feather
import pandas as pd
from tqdm.auto import tqdm

from solsim.system import BaseSystem, BaseSolanaSystem
from solsim.type import StateType


class Simulation:
    def __init__(self, system: Union[BaseSystem, BaseSolanaSystem], watchlist: Iterable[str], n_steps: int) -> None:
        self._system = system
        self._watchlist = set(watchlist)
        self._n_steps = n_steps

    def run(self, visualize_results: bool = False) -> pd.DataFrame:
        results = asyncio.run(self._run())
        if visualize_results:
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    app = self._start_results_app(results, tmpdir)
                    app.wait()
            except KeyboardInterrupt:
                pass
        return results

    @staticmethod
    def _start_results_app(results, tmpdir):
        results_path = os.path.join(tmpdir, "results.feather")
        feather.write_dataframe(results, results_path)
        env = {**os.environ, "SOLSIM_RESULTS_PATH": results_path}
        return subprocess.Popen(["streamlit", "run", "visualize.py"], cwd=os.path.dirname(__file__), env=env)

    async def _run(self) -> pd.DataFrame:
        try:
            state: StateType = {}
            history: list[StateType] = []
            results: list[StateType] = []
            for step in tqdm(range(-1, self._n_steps - 1), desc="Steps completed"):
                if self._system.uses_solana:
                    updates = await self._system.initialStep() if step == -1 else await self._system.step(state, history)  # type: ignore  # noqa: E501
                else:
                    updates = self._system.initialStep() if step == -1 else self._system.step(state, history)
                state = {**state, **updates, "step": step}
                history.append(state)
                results.append(self._filter_state(state))
        finally:
            if self._system.uses_solana:
                await self._system.tearDown()  # type: ignore
        results = pd.DataFrame(results)
        return self._reorder_results_columns(results)

    def _filter_state(self, state: StateType) -> StateType:
        for qty in self._watchlist:
            if qty not in state:
                raise Exception(f"{qty} not found in state: {state}")
        return {qty: state[qty] for qty in self._watchlist | {"step"}}

    @staticmethod
    def _reorder_results_columns(results: pd.DataFrame) -> pd.DataFrame:
        cols = ["step"] + sorted([col for col in results.columns if col != "step"])
        return results[cols]
