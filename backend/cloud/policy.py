from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse
import ipaddress
from .classification import CloudObject, DataClassification, CloudPermission, RedactionState, EncryptionState

class DeploymentProfile(str, Enum): LOCAL_ONLY="LOCAL_ONLY"; HYBRID_OPT_IN="HYBRID_OPT_IN"; MANAGED_TEAM="MANAGED_TEAM"
class Role(str, Enum): VIEWER="VIEWER"; ENGINEER="ENGINEER"; REVIEWER="REVIEWER"; LAB_OPERATOR="LAB_OPERATOR"; ADMIN="ADMIN"
class CloudAction(str, Enum): RETRIEVE_PUBLIC_SOURCE="RETRIEVE_PUBLIC_SOURCE"; OCR="OCR"; AI_REVIEW="AI_REVIEW"; ENCRYPTED_SYNC="ENCRYPTED_SYNC"; BACKUP="BACKUP"; CREATE_JOB="CREATE_JOB"; ACCEPT_CANDIDATE="ACCEPT_CANDIDATE"
@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool; permission: CloudPermission; requires_redaction: bool=False; requires_encryption: bool=False; requires_approval: bool=False; reason: str=""
@dataclass
class CloudPolicy:
    profile: DeploymentProfile=DeploymentProfile.LOCAL_ONLY
    provider_allowlist: set[str]=field(default_factory=set)
    model_allowlist: set[str]=field(default_factory=set)
    allowed_endpoints: set[str]=field(default_factory=set)
    reconstructible_allowed: bool=False
    def decide(self, obj: CloudObject, action: CloudAction) -> PolicyDecision:
        c=obj.classification
        if self.profile==DeploymentProfile.LOCAL_ONLY: return PolicyDecision(False,CloudPermission.DENY,reason="LOCAL_ONLY disables cloud")
        if c in {DataClassification.SECRET,DataClassification.HARDWARE_CONTROL}: return PolicyDecision(False,CloudPermission.DENY,reason=f"{c.value} denied")
        if c in {DataClassification.PUBLIC_SOURCE,DataClassification.PUBLIC_DERIVED}: return PolicyDecision(True,CloudPermission.ALLOW)
        if c is DataClassification.RECONSTRUCTIBLE: return PolicyDecision(self.reconstructible_allowed, CloudPermission.ALLOW if self.reconstructible_allowed else CloudPermission.DENY)
        if c is DataClassification.INTERNAL: return PolicyDecision(True,CloudPermission.APPROVAL_REQUIRED,requires_redaction=obj.redaction_state!=RedactionState.REDACTED,requires_approval=True)
        if c is DataClassification.CONFIDENTIAL: return PolicyDecision(True,CloudPermission.APPROVAL_REQUIRED,True,obj.encryption_state!=EncryptionState.ENCRYPTED,True)
        if c is DataClassification.AUTHORITATIVE_EVIDENCE:
            ok=action in {CloudAction.ENCRYPTED_SYNC,CloudAction.BACKUP}
            return PolicyDecision(ok, CloudPermission.ENCRYPTED_SYNC_ONLY if ok else CloudPermission.DENY, requires_encryption=obj.encryption_state!=EncryptionState.ENCRYPTED, requires_approval=True, reason="candidate/sync only")
        return PolicyDecision(False,CloudPermission.DENY)

def can(role: Role, action: CloudAction) -> bool:
    return role is Role.ADMIN or (action==CloudAction.CREATE_JOB and role in {Role.ENGINEER,Role.REVIEWER}) or (action==CloudAction.ACCEPT_CANDIDATE and role is Role.REVIEWER)

def endpoint_allowed(url: str, allowed_hosts: set[str]) -> bool:
    p=urlparse(url)
    if p.scheme!="https" or p.username or p.password or (p.port not in (None,443)): return False
    host=p.hostname or ""
    if host not in allowed_hosts: return False
    try:
        ip=ipaddress.ip_address(host)
        if ip.is_loopback or ip.is_link_local or ip.is_private: return False
    except ValueError: pass
    return True
