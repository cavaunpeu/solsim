from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, Set

class BaseSystem(ABC):

  @abstractmethod
  def step(self) -> Dict:
    raise NotImplementedError