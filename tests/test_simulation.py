from solsim.simulation import Simulation


def mock_run_method(num_runs, visualize_results):
    return num_runs, visualize_results


def test_cli_command_list():
    simulation = Simulation(system=None, watchlist=(), n_steps=1)
    expected_cli_commands = ["run"]
    actual_cli_commands = [cmd.callback.__name__ for cmd in simulation.cli.registered_commands]
    assert actual_cli_commands == expected_cli_commands


def test_cli_run_method(mocker):
    mocker.patch.object(Simulation, "run", side_effect=mock_run_method)
    simulation = Simulation(system=None, watchlist=(), n_steps=1)
    cli_commands = simulation.cli.registered_commands
    (cli_run_cmd,) = [cmd.callback for cmd in cli_commands if cmd.callback.__name__ == "run"]
    args = 123, True
    assert simulation.run(*args) == cli_run_cmd(*args)
    assert Simulation.run.mock_calls == [mocker.call(*args)] * 2
