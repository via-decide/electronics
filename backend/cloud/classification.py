from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from hashlib import sha256
from typing import Any, Mapping

class DataClassification(str, Enum):
    PUBLIC_SOURCE="PUBLIC_SOURCE"; PUBLIC_DERIVED="PUBLIC_DERIVED"; INTERNAL="INTERNAL"; CONFIDENTIAL="CONFIDENTIAL"; SECRET="SECRET"; HARDWARE_CONTROL="HARDWARE_CONTROL"; AUTHORITATIVE_EVIDENCE="AUTHORITATIVE_EVIDENCE"; RECONSTRUCTIBLE="RECONSTRUCTIBLE"

class RedactionState(str, Enum): NONE="NONE"; REQUIRED="REQUIRED"; REDACTED="REDACTED"
class EncryptionState(str, Enum): NONE="NONE"; REQUIRED="REQUIRED"; ENCRYPTED="ENCRYPTED"
class CloudPermission(str, Enum): ALLOW="ALLOW"; DENY="DENY"; APPROVAL_REQUIRED="APPROVAL_REQUIRED"; ENCRYPTED_SYNC_ONLY="ENCRYPTED_SYNC_ONLY"

@dataclass(frozen=True)
class CloudObject:
    object_id: str; project_id: str; board_revision: str; classification: DataClassification
    owner: str; tenant: str; source: str; content_hash: str
    redaction_state: RedactionState = RedactionState.NONE
    encryption_state: EncryptionState = EncryptionState.NONE
    retention_policy: str = "LOCAL_DEFAULT"
    cloud_permission: CloudPermission = CloudPermission.DENY
    approval_record: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d=asdict(self); d["classification"]=self.classification.value; d["redaction_state"]=self.redaction_state.value; d["encryption_state"]=self.encryption_state.value; d["cloud_permission"]=self.cloud_permission.value; return d

def content_hash(data: bytes | str) -> str:
    if isinstance(data, str): data=data.encode()
    return "sha256:"+sha256(data).hexdigest()

def classify_payload(payload: Mapping[str, Any], *, default: DataClassification=DataClassification.INTERNAL) -> DataClassification:
    text=str(payload).lower()
    if any(k in text for k in ["jtag","gpio","swd","power_relay","firmware_flash","storage_erase"]): return DataClassification.HARDWARE_CONTROL
    if any(k in text for k in ["private key","password","api_key","secret","credential","signing key"]): return DataClassification.SECRET
    if any(k in text for k in ["schematic","board image","measurement","bench_verified","authoritative"]): return DataClassification.AUTHORITATIVE_EVIDENCE
    if payload.get("public") is True or str(payload.get("source","")).startswith(("http://","https://")): return DataClassification.PUBLIC_SOURCE
    return default
