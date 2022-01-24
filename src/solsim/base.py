from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, Set, List, Any

from anchorpy import create_workspace, close_workspace

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

  def __init__(self, workspace_dir):
    self.workspace = create_workspace(workspace_dir)

  @property
  def uses_solana(self):
    return True

  async def tearDown(self):
    await close_workspace(self.workspace)
