#!/usr/bin/env python3
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path
REQ = ['Makefile','CMakeLists.txt','CMakePresets.json','requirements.lock','.tool-versions','docker/ci.Dockerfile','.github/workflows/ci.yml','projects/ssd_lab/firmware/CMakeLists.txt','simulator/ssd/src/ssd_sim/nand.py','firmware/storage/CMakeLists.txt']
def sha(p):
    h=hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--strict',action='store_true'); ap.add_argument('--format-check',action='store_true'); ap.add_argument('--lint',action='store_true'); ap.add_argument('--emit-manifest'); ap.add_argument('paths',nargs='*'); a=ap.parse_args()
    miss=[p for p in REQ if not Path(p).exists()]
    if miss: print('missing '+','.join(miss)); return 1
    bad=[]
    for p in ['docker/ci.Dockerfile','requirements.lock','pyproject.toml']:
        s=Path(p).read_text()
        if ':latest' in s or '@main' in s or '>=' in s: bad.append(p)
    if bad: print('floating dependencies '+','.join(bad)); return 1
    if a.emit_manifest:
        files=[]
        for root in a.paths or ['build/host']:
            rp=Path(root)
            if rp.is_file(): files.append(rp)
            elif rp.exists(): files += [p for p in rp.rglob('*') if p.is_file()]
        data={'versions':{},'artifacts':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)]}
        for cmd in ['python3 --version','cmake --version','gcc --version']:
            try: data['versions'][cmd]=subprocess.check_output(cmd.split(),text=True).splitlines()[0]
            except Exception as e: data['versions'][cmd]=str(e)
        Path(a.emit_manifest).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    return 0
if __name__=='__main__': sys.exit(main())
