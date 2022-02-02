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

    def __init__(self, system: Union[BaseSystem, BaseSolanaSystem], watchlist: Iterable[str]) -> None:
        self._system = system
        self._watchlist = set(watchlist)

    @property
    def cli(self) -> typer.Typer:
        app = typer.Typer()

        @app.command()  # type: ignore
        def run(runs: int = 1, steps_per_run: int = 1, viz_results: bool = False) -> pd.DataFrame:
            return self.run(runs, steps_per_run, viz_results)

        @app.callback()  # type: ignore
        def callback() -> None:
            pass

        return app

    def run(self, runs: int = 1, steps_per_run: int = 3, visualize_results: bool = False) -> pd.DataFrame:
        """Run your simulation.

        Args:
            runs: The number of times to run your simulation.
            visualize_results: Optionally build and start a Streamlit app to explore simulation results.

        Returns:
            results: A pandas DataFrame containing your simulation results.
        """
        results = asyncio.run(self._run(runs, steps_per_run))
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

    async def _run(self, runs: int, steps_per_run: int) -> pd.DataFrame:
        results: list[StateType] = []
        try:
            for run in range(runs):
                try:
                    state: StateType = {}
                    history: list[StateType] = []
                    self._system.setup()
                    for step in tqdm(range(steps_per_run), desc=f"🟢 run: {run} | step"):
                        if self._system.uses_solana:
                            updates = await self._system.initial_step() if step == 0 else await self._system.step(state, history)  # type: ignore  # noqa: E501
                        else:
                            updates = self._system.initial_step() if step == 0 else self._system.step(state, history)
                        state = {**state, **updates, "run": run, "step": step}
                        history.append(state)
                        results.append(self._filter_state(state))
                finally:
                    self._system.teardown()
        finally:
            await self._system.cleanup() if self._system.uses_solana else self._system.cleanup()

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
