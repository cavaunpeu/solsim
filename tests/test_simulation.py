from solsim.simulation import Simulation


def mock_run_method(num_runs, num_steps_per_run, visualize_results):
    return num_runs, num_steps_per_run, visualize_results


def test_cli_command_list():
    simulation = Simulation(system=None, watchlist=())
    expected_cli_commands = ["run"]
    actual_cli_commands = [cmd.callback.__name__ for cmd in simulation.cli.registered_commands]
    assert actual_cli_commands == expected_cli_commands


def test_cli_run_method(mocker):
    mocker.patch.object(Simulation, "run", side_effect=mock_run_method)
    simulation = Simulation(system=None, watchlist=())
    cli_commands = simulation.cli.registered_commands
    (cli_run_cmd,) = [cmd.callback for cmd in cli_commands if cmd.callback.__name__ == "run"]
    args = 5, 10, True  # runs, steps_per_run, viz_results
    assert simulation.run(*args) == cli_run_cmd(*args)
    assert Simulation.run.mock_calls == [mocker.call(*args)] * 2
