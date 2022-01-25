from abc import ABC, abstractmethod
from typing import Awaitable, Dict, Optional, Set, List, Any, Union

from anchorpy import create_workspace, close_workspace
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc import commitment

from solsim.type import StateType


class BaseSystem(ABC):
    @abstractmethod
    def initialStep(self) -> Awaitable[Any]:
        raise NotImplementedError

    @abstractmethod
    def step(self, state: StateType, history: List[StateType]) -> Awaitable[Any]:
        raise NotImplementedError


class BaseSolanaSystem(BaseSystem):

    SOLANA_CLUSTER_URI = "http://127.0.0.1:8899"

    def __init__(self, workspace_dir: str, client: Optional[Client] = None) -> None:
        self.workspace = create_workspace(workspace_dir)
        self.client = client or Client(self.SOLANA_CLUSTER_URI)

    async def tearDown(self) -> None:
        await close_workspace(self.workspace)

    def get_token_account_balance(
        self, pubkey: PublicKey, commitment: Optional[commitment.Commitment] = commitment.Confirmed
    ) -> float:
        return float(self.client.get_token_account_balance(pubkey, commitment)["result"]["value"]["uiAmount"])
