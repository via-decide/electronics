from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from datetime import datetime, timezone, timedelta
from typing import Any
from .policy import CloudPolicy, CloudAction
from .classification import CloudObject, DataClassification
from .audit import AppendOnlyAuditLog, AuditEventType
HARDWARE_CAPABILITIES={"GPIO","JTAG","SWD","PROGRAMMER","POWER_RELAY","OSCILLOSCOPE_CONTROL","LOGIC_ANALYZER_CONTROL","SERIAL_CONSOLE_WRITE","STORAGE_PROGRAM","STORAGE_ERASE","FIRMWARE_FLASH"}
DISALLOWED_TASKS={"component_confirmation","electrical_approval","BENCH_VERIFIED","hardware_authorization","firmware_flashing","power_operation","erase_commands"}
class JobState(str, Enum):
    DRAFT="DRAFT"; AWAITING_APPROVAL="AWAITING_APPROVAL"; APPROVED="APPROVED"; REDACTING="REDACTING"; ENCRYPTING="ENCRYPTING"; QUEUED="QUEUED"; RUNNING="RUNNING"; RESULT_RECEIVED="RESULT_RECEIVED"; VALIDATING="VALIDATING"; REVIEW_REQUIRED="REVIEW_REQUIRED"; ACCEPTED="ACCEPTED"; REJECTED="REJECTED"; CANCELLED="CANCELLED"; FAILED="FAILED"; EXPIRED="EXPIRED"
@dataclass
class CloudJob:
    job_id: str; project_id: str; board_revision: str; requesting_user: str; provider: str; model_or_parser_id: str; task: str; inputs: list[CloudObject]
    state: JobState=JobState.DRAFT; approval: str|None=None; redaction_manifest: list[dict[str,Any]]=field(default_factory=list); request_hash: str|None=None; result_hash: str|None=None; cost: dict[str,Any]=field(default_factory=dict); created_time: str=field(default_factory=lambda: datetime.now(timezone.utc).isoformat()); expiry: str=field(default_factory=lambda: (datetime.now(timezone.utc)+timedelta(hours=24)).isoformat()); audit_events: list[str]=field(default_factory=list)
    def serialize_request(self):
        if self.task in DISALLOWED_TASKS: raise ValueError("disallowed cloud AI task")
        for obj in self.inputs:
            if obj.classification in {DataClassification.SECRET,DataClassification.HARDWARE_CONTROL}: raise ValueError("secret/hardware object blocked before serialization")
        req={"job_id":self.job_id,"project_id":self.project_id,"board_revision":self.board_revision,"task":self.task,"model":self.model_or_parser_id,"input_object_hashes":[o.content_hash for o in self.inputs]}
        self.request_hash="sha256:"+sha256(str(req).encode()).hexdigest(); return req
class CloudJobService:
    hardware_capabilities=frozenset()
    def __init__(self, policy: CloudPolicy, audit: AppendOnlyAuditLog): self.policy=policy; self.audit=audit; self.jobs={}
    def queue(self, job: CloudJob):
        if self.hardware_capabilities & HARDWARE_CAPABILITIES: raise RuntimeError("CloudService intersects hardware capabilities")
        for obj in job.inputs:
            d=self.policy.decide(obj, CloudAction.CREATE_JOB)
            if not d.allowed or d.requires_approval and not job.approval: self.audit.append(AuditEventType.UPLOAD_REJECTED,job.requesting_user,obj.object_id,reason=d.reason); raise PermissionError(d.reason or "approval required")
        job.serialize_request(); job.state=JobState.QUEUED; rec=self.audit.append(AuditEventType.CLOUD_JOB_QUEUED,job.requesting_user,job.job_id); job.audit_events.append(rec.record_hash); self.jobs[job.job_id]=job; return job
