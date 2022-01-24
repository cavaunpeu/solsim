from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, Set, List, Any

class BaseSystem(ABC):

  @abstractmethod
  def initialStep(self) -> Dict:
    raise NotImplementedError

  @abstractmethod
  def step(self, state: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict:
    raise NotImplementedError