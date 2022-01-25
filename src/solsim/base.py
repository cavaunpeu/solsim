from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, Set, List, Any

from anchorpy import create_workspace, close_workspace
from solana.publickey import PublicKey
from solana.rpc.api import Client

class BaseSystem(ABC):

  @property
  def uses_solana(self):
    return False

  @abstractmethod
  def initialStep(self) -> Dict:
    raise NotImplementedError

  @abstractmethod
  def step(self, state: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict:
    raise NotImplementedError


class BaseSolanaSystem(BaseSystem):

  SOLANA_CLUSTER_URI = "http://127.0.0.1:8899"

  def __init__(self, workspace_dir, client=None):
    self.workspace = create_workspace(workspace_dir)
    self.client = client or Client(self.SOLANA_CLUSTER_URI)

  @property
  def uses_solana(self):
    return True

  async def tearDown(self):
    await close_workspace(self.workspace)

  def get_token_account_balance(self, pubkey: PublicKey, commitment='confirmed') -> float:
    return self.client.get_token_account_balance(pubkey, commitment)['result']['value']['uiAmount']
