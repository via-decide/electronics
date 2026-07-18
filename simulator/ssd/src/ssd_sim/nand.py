import random
from .page import PageState
from .trace import Trace, data_hash
class Nand:
    def __init__(self, geometry, profile_hash, seed=1):
        self.g=geometry; self.profile_hash=profile_hash; self.seed=seed; self.rng=random.Random(seed); self.seq=0; self.write_enable=False; self.busy_until=0; self.media=[bytearray([0xff])*geometry.page_size for _ in range(geometry.page_count)]; self.state=[PageState.ERASED for _ in range(geometry.page_count)]; self.trace=Trace(); self.host_writes=0; self.media_writes=0; self.erase_counts=[0]*(geometry.dies*geometry.blocks_per_die)
    def _ev(self, cmd, addr=None, pre=None, post=None, status='OK', fault=None, data=b'', timing=0):
        self.seq+=1; self.trace.add(seed=self.seed, sequence=self.seq, command=cmd, address=addr, **{'pre-state':str(pre), 'post-state':str(post), 'status-register result':status, 'fault injected':fault, 'timing':timing, 'data hash':data_hash(data), 'profile hash':self.profile_hash})
    def wen(self): self.write_enable=True; self._ev('WRITE_ENABLE')
    def read(self, ppn):
        st=self.state[ppn]; status='ECC_UNCORRECTABLE' if st==PageState.UNCORRECTABLE else 'OK'; data=bytes(self.media[ppn]); self._ev('READ',ppn,st,st,status,None,data,50); return data,status
    def program(self, ppn, data):
        pre=self.state[ppn]
        if not self.write_enable: self._ev('PROGRAM',ppn,pre,pre,'FAIL_MISSING_WEL'); return 'FAIL_MISSING_WEL'
        old=self.media[ppn]; nd=bytes([old[i] & data[i%len(data)] for i in range(len(old))]); self.media[ppn]=bytearray(nd); self.state[ppn]=PageState.PROGRAMMED_VALID; self.write_enable=False; self.media_writes+=1; self.host_writes+=1; self._ev('PROGRAM',ppn,pre,self.state[ppn],'OK',None,nd,300); return 'OK'
    def erase(self, block):
        pre='BLOCK'; start=block*self.g.pages_per_block
        if not self.write_enable: self._ev('ERASE',block,pre,pre,'FAIL_MISSING_WEL'); return 'FAIL_MISSING_WEL'
        for i in range(start,start+self.g.pages_per_block): self.media[i]=bytearray([0xff])*self.g.page_size; self.state[i]=PageState.ERASED
        self.erase_counts[block]+=1; self.write_enable=False; self._ev('ERASE',block,pre,'ERASED','OK',None,b'',2000); return 'OK'
    def metrics(self): return {'host_writes':self.host_writes,'media_writes':self.media_writes,'write_amplification':self.media_writes/max(1,self.host_writes),'erase_counts':self.erase_counts}
