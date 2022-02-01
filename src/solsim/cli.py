import pandas as pd
import typer

from solsim.simulation import Simulation


def build_cli(simulation: Simulation) -> typer.Typer:
    app = typer.Typer()

    @app.command()
    def run(num_runs: int = 1, viz_results: bool = False) -> pd.DataFrame:
        return simulation.run(num_runs, viz_results)

    @app.callback()
    def callback() -> None:
        pass

    return app
