from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Any

class AuditEventType(str, Enum):
    CLOUD_PROFILE_CHANGED="CLOUD_PROFILE_CHANGED"; OBJECT_CLASSIFIED="OBJECT_CLASSIFIED"; UPLOAD_REQUESTED="UPLOAD_REQUESTED"; UPLOAD_APPROVED="UPLOAD_APPROVED"; UPLOAD_REJECTED="UPLOAD_REJECTED"; REDACTION_APPLIED="REDACTION_APPLIED"; OBJECT_ENCRYPTED="OBJECT_ENCRYPTED"; CLOUD_JOB_QUEUED="CLOUD_JOB_QUEUED"; CLOUD_JOB_CANCELLED="CLOUD_JOB_CANCELLED"; CLOUD_RESULT_RECEIVED="CLOUD_RESULT_RECEIVED"; CLOUD_RESULT_REJECTED="CLOUD_RESULT_REJECTED"; CLOUD_RESULT_ACCEPTED_AS_CANDIDATE="CLOUD_RESULT_ACCEPTED_AS_CANDIDATE"; SYNC_COMPLETED="SYNC_COMPLETED"; SYNC_FAILED="SYNC_FAILED"; REMOTE_COPY_DELETION_REQUESTED="REMOTE_COPY_DELETION_REQUESTED"; REMOTE_COPY_DELETED="REMOTE_COPY_DELETED"; PROVIDER_DISABLED="PROVIDER_DISABLED"; HARDWARE_CAPABILITY_BLOCKED="HARDWARE_CAPABILITY_BLOCKED"
@dataclass(frozen=True)
class AuditRecord:
    event_type: AuditEventType; actor: str; object_id: str|None; details: dict[str, Any]; timestamp: str; previous_hash: str; record_hash: str
class AppendOnlyAuditLog:
    def __init__(self): self._records=[]
    def append(self, event_type: AuditEventType, actor: str, object_id: str|None=None, **details):
        prev=self._records[-1].record_hash if self._records else "GENESIS"
        ts=datetime.now(timezone.utc).isoformat()
        body=f"{event_type.value}|{actor}|{object_id}|{details}|{ts}|{prev}"
        rec=AuditRecord(event_type,actor,object_id,details,ts,prev,sha256(body.encode()).hexdigest())
        self._records.append(rec); return rec
    @property
    def records(self): return tuple(self._records)
