from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import re
from typing import Any
@dataclass(frozen=True)
class RedactionEntry:
    field_path: str; redaction_rule: str; replacement_token: str; original_hash: str; review_status: str="PENDING_REVIEW"
PATTERNS=[("PRIVATE_KEY",re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",re.S)),("EMAIL",re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),("API_KEY",re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{8,})")),("PASSWORD",re.compile(r"(?i)password\s*[:=]\s*['\"]?([^\s,'\"]+)")),("INTERNAL_URL",re.compile(r"https?://(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[0-1])\.\d+\.\d+)[^\s]*")),("PATH",re.compile(r"(?:/[A-Za-z0-9._-]+){2,}")),("SERIAL",re.compile(r"(?i)(serial|device[_ -]?id)\s*[:=]\s*([A-Za-z0-9-]{6,})")),("WIFI",re.compile(r"(?i)(ssid|wifi|wpa_psk)\s*[:=]\s*([^\s,]+)"))]
def _token(rule, val): return f"<REDACTED:{rule}:{sha256(val.encode()).hexdigest()[:12]}>"
def redact_text(text: str, field_path: str="$"):
    manifest=[]
    for rule, pat in PATTERNS:
        def repl(m):
            original=m.group(0); tok=_token(rule, original)
            manifest.append(RedactionEntry(field_path,rule,tok,"sha256:"+sha256(original.encode()).hexdigest()))
            return tok
        text=pat.sub(repl,text)
    return text, [asdict(x) for x in manifest]
def redact_object(obj: Any, path: str="$"):
    if isinstance(obj, str): return redact_text(obj,path)
    if isinstance(obj, dict):
        out={}; man=[]
        for k,v in obj.items(): out[k], m=redact_object(v,f"{path}.{k}"); man.extend(m)
        return out, man
    if isinstance(obj, list):
        out=[]; man=[]
        for i,v in enumerate(obj): rv,m=redact_object(v,f"{path}[{i}]"); out.append(rv); man.extend(m)
        return out, man
    return obj, []
