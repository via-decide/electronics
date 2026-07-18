#!/usr/bin/env python3
import argparse, hashlib, sys, yaml
from pathlib import Path
REQ=['evidence_id','fixture_id','board_revision','firmware_commit','nand_profile_sha256','instrument','raw_artifact_path','sha256','acquisition_timestamp','procedure','measured_values','limits','result','human_reviewer','classification']
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('--strict',action='store_true'); a=ap.parse_args(); root=Path(a.dir); real=0; errs=[]
 for f in root.rglob('*.yaml'):
  d=yaml.safe_load(f.read_text())
  for k in REQ:
   if k not in d: errs.append(f'{f}: missing {k}')
  raw=root/d.get('raw_artifact_path','')
  if raw.exists() and hashlib.sha256(raw.read_bytes()).hexdigest()!=d.get('sha256'): errs.append(f'{f}: hash mismatch')
  if d.get('classification')=='REAL_MEASUREMENT' and d.get('result')=='PASS': real+=1
  if d.get('classification')=='SYNTHETIC_EXAMPLE' and d.get('human_reviewer')!='SYNTHETIC_EXAMPLE': errs.append(f'{f}: synthetic mislabeled')
 if errs: print('\n'.join(errs)); return 1
 print(f'evidence validation passed; real_pass_count={real}')
 return 0
if __name__=='__main__': sys.exit(main())
