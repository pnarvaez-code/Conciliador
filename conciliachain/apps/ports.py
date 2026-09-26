from abc import ABC, abstractmethod
from ..models import Record
class Port(ABC):
    name = "port"
    @abstractmethod
    def fetch(self) -> list[Record]: ...
