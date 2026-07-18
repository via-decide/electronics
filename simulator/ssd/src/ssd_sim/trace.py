import json, hashlib
def data_hash(data): return hashlib.sha256(data or b'').hexdigest()
class Trace:
    def __init__(self): self.events=[]
    def add(self, **kw): self.events.append(kw)
    def save(self,p): open(p,'w').write(json.dumps(self.events,indent=2,sort_keys=True)+'\n')
    @staticmethod
    def load(p): return json.load(open(p))
