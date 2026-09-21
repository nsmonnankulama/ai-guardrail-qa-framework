from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ConnectorResponse:
    response_text: str
    latency_ms: float
    raw: Any = None
    error: Optional[str] = None


class BaseConnector(ABC):
    def __init__(self, config: dict):
        self.config = config or {}

    @abstractmethod
    def send(self, prompt: str, system_prompt: str = "") -> ConnectorResponse:
        raise NotImplementedError
