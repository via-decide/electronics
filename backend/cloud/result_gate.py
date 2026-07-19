from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Any
PROHIBITED={"CONFIRMED_COMPONENT","CONFIRMED_OFFICIAL_FACT","ELECTRICALLY_APPROVED","REPAIR_VERIFIED","BENCH_VERIFIED","FIRMWARE_AUTHORIZED","flash_firmware","erase_storage","operate_hardware"}
INJECTION=["ignore previous instructions","system prompt","call gpio","jtag","flash firmware","erase storage","power relay"]
class CloudOutputState(str, Enum): CANDIDATE="CANDIDATE"; REVIEW_REQUIRED="REVIEW_REQUIRED"; REJECTED="REJECTED"
@dataclass(frozen=True)
class GateDecision: state: CloudOutputState; reasons: list[str]
def validate_cloud_result(result: dict[str,Any], *, request_hash: str, provider: str, model: str, provider_allowlist: set[str], model_allowlist: set[str]) -> GateDecision:
    reasons=[]
    if provider not in provider_allowlist: reasons.append("provider not allowlisted")
    if model not in model_allowlist: reasons.append("model not allowlisted")
    if result.get("request_hash") != request_hash: reasons.append("request-result binding failed")
    if result.get("state") not in {"CANDIDATE","REVIEW_REQUIRED"}: reasons.append("invalid candidate state")
    text=str(result).lower()
    if any(x.lower() in text for x in PROHIBITED): reasons.append("prohibited authoritative/hardware output")
    if any(x in text for x in INJECTION): reasons.append("prompt-injection payload detected")
    if not isinstance(result.get("findings",[]), list): reasons.append("schema validation failed")
    return GateDecision(CloudOutputState.REJECTED if reasons else CloudOutputState.REVIEW_REQUIRED, reasons or ["schema validated candidate requires local human review"])
def result_hash(result): return "sha256:"+sha256(str(result).encode()).hexdigest()
