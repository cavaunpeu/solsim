import typer


def build_cli(simulation):
    app = typer.Typer()

    @app.command()
    def run(num_runs: int = 1, viz_results: bool = False):
        return simulation.run(num_runs, viz_results)

    @app.callback()
    def callback():
        pass

    return app
