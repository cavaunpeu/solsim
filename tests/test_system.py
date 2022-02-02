import os
from signal import SIGTERM
from pytest import fixture
from typing import Any, Dict, List

from solana.keypair import Keypair
from solana.publickey import PublicKey

import solsim
from solsim.simulation import Simulation
from solsim.system import BaseSolanaSystem


class SomeSolanaSystem(BaseSolanaSystem):
    def __init__(self, workspace_dir, client, localnet_process):
        super().__init__(workspace_dir, client=client, localnet_process=localnet_process)

    async def initial_step(self) -> Dict:
        return {"a": 1}

    async def step(self, state: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict:
        return {"a": 1, "b": 2}


@fixture(scope="function")
def workspace_dir():
    return os.path.join(os.path.dirname(__file__), "idls")


@fixture(scope="function")
def solana_localnet_process(mocker):
    p = mocker.Mock()
    p.configure_mock(pid=123)
    p.children.return_value = []
    return p


@fixture(scope="function")
def solana_client():
    class DummySolanaClient:
        def __init__(self) -> None:
            pass

        def get_token_account_balance(self, pubkey: PublicKey, commitment: str):
            return {"result": {"value": {"uiAmount": 10}}}

    return DummySolanaClient()


def test_get_token_account_balance(workspace_dir, solana_client, solana_localnet_process):
    system = SomeSolanaSystem(workspace_dir, solana_client, solana_localnet_process)
    expected = 10
    actual = system.get_token_account_balance(pubkey=Keypair(), commitment="confirmed")

    assert actual == expected


def test_solana_localnet_process(mocker, workspace_dir, solana_client, solana_localnet_process):
    mocker.patch("psutil.Process", return_value=solana_localnet_process)
    system = SomeSolanaSystem(workspace_dir, solana_client, solana_localnet_process)
    simulation = Simulation(system, watchlist=("a"))
    simulation.run(num_steps_per_run=5)

    solana_localnet_process.send_signal.assert_called_once_with(SIGTERM)


def test_workspace_created_and_closed(mocker, workspace_dir, solana_client, solana_localnet_process):
    workspace = mocker.MagicMock()
    mocker.patch("psutil.Process", return_value=solana_localnet_process)
    mocker.patch("solsim.system.create_workspace", return_value=workspace)
    mocker.patch("solsim.system.close_workspace")
    system = SomeSolanaSystem(workspace_dir, solana_client, solana_localnet_process)

    solsim.system.create_workspace.assert_called_once_with(workspace_dir)

    simulation = Simulation(system, watchlist=("a"))
    simulation.run(num_steps_per_run=5)

    solsim.system.close_workspace.assert_called_once_with(workspace)
