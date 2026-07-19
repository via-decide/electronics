from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
class SyncState(str, Enum): PENDING="PENDING"; SYNCED="SYNCED"; CONFLICT="CONFLICT"; DELETE_REQUESTED="DELETE_REQUESTED"; DELETED="DELETED"
@dataclass
class SyncManifest:
    tenant: str; project_id: str; board_revision: str; version: int=1; encrypted_blobs: dict[str,dict[str,Any]]=field(default_factory=dict); tombstones: set[str]=field(default_factory=set); state: SyncState=SyncState.PENDING
    def add_blob(self, object_id, encrypted_blob):
        if "ciphertext" not in encrypted_blob or "key_ref" in encrypted_blob and "ciphertext" in encrypted_blob.get("key_ref",{}): raise ValueError("invalid encrypted blob")
        self.encrypted_blobs[object_id]=encrypted_blob; self.version+=1
    def detect_conflict(self, remote_version:int):
        if remote_version>self.version: self.state=SyncState.CONFLICT; return True
        return False
    def request_delete(self, object_id): self.tombstones.add(object_id); self.state=SyncState.DELETE_REQUESTED; self.version+=1
