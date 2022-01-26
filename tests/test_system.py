import os
from pytest import fixture
from typing import Any, Dict, List

from solana.keypair import Keypair
from solana.publickey import PublicKey

from solsim.system import BaseSolanaSystem


@fixture(scope="function")
def solana_client():
    class DummySolanaClient:
        def __init__(self) -> None:
            pass

        def get_token_account_balance(self, pubkey: PublicKey, commitment: str):
            return {"result": {"value": {"uiAmount": 10}}}

    return DummySolanaClient()


@fixture(scope="function")
def solana_system(solana_client):
    class SomeSolanaSystem(BaseSolanaSystem):
        def __init__(self, workspace_dir=os.path.join(os.path.dirname(__file__), "idls")):
            super().__init__(workspace_dir, client=solana_client, start_localnet=False)

        def initialStep(self) -> Dict:
            return {"a": 1}

        def step(self, state: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict:
            return {"a": 1, "b": 2}

    return SomeSolanaSystem()


def test_get_token_account_balance(solana_system):
    expected = 10
    actual = solana_system.get_token_account_balance(pubkey=Keypair(), commitment="confirmed")
    assert actual == expected
