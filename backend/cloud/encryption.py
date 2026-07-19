from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import hmac, os, base64, json
@dataclass(frozen=True)
class KeyRef: tenant: str; project_id: str; key_id: str; version: int
class KeyStore:
    def __init__(self): self._keys={}
    def create_project_key(self, tenant, project_id):
        ref=KeyRef(tenant,project_id,f"{tenant}:{project_id}:v1",1); self._keys[ref.key_id]=os.urandom(32); return ref
    def rotate(self, ref):
        n=KeyRef(ref.tenant,ref.project_id,f"{ref.tenant}:{ref.project_id}:v{ref.version+1}",ref.version+1); self._keys[n.key_id]=os.urandom(32); return n
    def get(self, ref): return self._keys[ref.key_id]
def _stream(key, nonce, n):
    out=b""; i=0
    while len(out)<n: out+=hmac.new(key,nonce+i.to_bytes(8,'big'),sha256).digest(); i+=1
    return out[:n]
def encrypt(plaintext: bytes, ref: KeyRef, store: KeyStore, associated_data: dict):
    key=store.get(ref); nonce=os.urandom(12); ad=json.dumps(associated_data,sort_keys=True).encode(); ct=bytes(a^b for a,b in zip(plaintext,_stream(key,nonce,len(plaintext))))
    tag=hmac.new(key,ad+nonce+ct,sha256).digest()
    return {"schema_version":"cloud-encrypted-blob/v1","key_ref":asdict(ref),"associated_data":associated_data,"nonce":base64.b64encode(nonce).decode(),"ciphertext":base64.b64encode(ct).decode(),"tag":base64.b64encode(tag).decode()}
def decrypt(blob, store: KeyStore):
    ref=KeyRef(**blob["key_ref"]); key=store.get(ref); ad=json.dumps(blob["associated_data"],sort_keys=True).encode(); nonce=base64.b64decode(blob["nonce"]); ct=base64.b64decode(blob["ciphertext"]); tag=base64.b64decode(blob["tag"])
    if not hmac.compare_digest(tag,hmac.new(key,ad+nonce+ct,sha256).digest()): raise ValueError("integrity verification failed")
    return bytes(a^b for a,b in zip(ct,_stream(key,nonce,len(ct))))
