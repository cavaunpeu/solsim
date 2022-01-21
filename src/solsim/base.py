from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, Set

class BaseSystem(ABC):

  @abstractproperty
  def quantities(self) -> Set:
    raise NotImplementedError

  @abstractmethod
  def step(self) -> Dict:
    raise NotImplementedError