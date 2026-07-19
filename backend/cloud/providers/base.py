from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any
@dataclass(frozen=True)
class ProviderResult: provider: str; model: str; request_hash: str; payload: dict[str, Any]; uploaded_bytes: int=0; downloaded_bytes: int=0; estimated_cost: float|None=None
class CloudProvider(Protocol):
    name: str
    allowed_models: set[str]
    def submit(self, request: dict[str, Any]) -> ProviderResult: ...
