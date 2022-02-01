import asyncio
from collections.abc import Iterable
import os
import subprocess
import tempfile
from typing import Any, Union

import feather
import pandas as pd
from tqdm.auto import tqdm
import typer

from solsim.system import BaseSystem, BaseSolanaSystem
from solsim.type import StateType


class Simulation:

    INDEX_COLS = ["step", "run"]

    def __init__(self, system: Union[BaseSystem, BaseSolanaSystem], watchlist: Iterable[str], n_steps: int) -> None:
        self._system = system
        self._watchlist = set(watchlist)
        self._n_steps = n_steps

    @property
    def cli(self) -> typer.Typer:
        app = typer.Typer()

        @app.command()  # type: ignore
        def run(num_runs: int = 1, viz_results: bool = False) -> pd.DataFrame:
            return self.run(num_runs, viz_results)

        @app.callback()  # type: ignore
        def callback() -> None:
            pass

        return app

    def run(self, num_runs: int = 1, visualize_results: bool = False) -> pd.DataFrame:
        """Run your simulation.

        Args:
            num_runs: The number of times to run your simulation.
            visualize_results: Optionally build and start a Streamlit app to explore simulation results.

        Returns:
            results: A pandas DataFrame containing your simulation results.
        """
        results = asyncio.run(self._run(num_runs))
        if visualize_results:
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    app = self._start_results_app(results, tmpdir)
                    app.wait()
            except KeyboardInterrupt:
                pass
        return results

    @staticmethod
    def _start_results_app(results: pd.DataFrame, tmpdir: str) -> subprocess.Popen[Any]:
        results_path = os.path.join(tmpdir, "results.feather")
        feather.write_dataframe(results, results_path)
        env = {**os.environ, "SOLSIM_RESULTS_PATH": results_path}
        return subprocess.Popen(["streamlit", "run", "visualize.py"], cwd=os.path.dirname(__file__), env=env)

    async def _run(self, num_runs: int) -> pd.DataFrame:
        try:
            state: StateType = {}
            history: list[StateType] = []
            results: list[StateType] = []
            for run in range(num_runs):
                for step in tqdm(range(self._n_steps), desc=f"run: {run} | step"):
                    if self._system.uses_solana:
                        updates = await self._system.initialStep() if step == 0 else await self._system.step(state, history)  # type: ignore  # noqa: E501
                    else:
                        updates = self._system.initialStep() if step == 0 else self._system.step(state, history)
                    state = {**state, **updates, "run": run, "step": step}
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
        return {qty: state[qty] for qty in self._watchlist | set(self.INDEX_COLS)}

    def _reorder_results_columns(self, results: pd.DataFrame) -> pd.DataFrame:
        cols = self.INDEX_COLS + sorted([col for col in results.columns if col not in self.INDEX_COLS])
        return results[cols]
