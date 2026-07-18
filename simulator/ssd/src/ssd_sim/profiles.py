import hashlib, yaml
from .geometry import Geometry
def load_profile(path):
    raw=open(path,'rb').read(); d=yaml.safe_load(raw)
    g=Geometry(**d['geometry']); return d,g,hashlib.sha256(raw).hexdigest()
def verify_profile(path):
    d,g,h=load_profile(path); assert g.page_count>0 and d.get('timing_us'); return h
