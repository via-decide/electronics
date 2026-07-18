#!/usr/bin/env python3
import argparse,json,yaml
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('--platform',required=True); ap.add_argument('--evidence',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
p=yaml.safe_load(open(a.platform)); real=[]
for f in Path(a.evidence).rglob('*.yaml'):
 d=yaml.safe_load(f.read_text())
 if d.get('classification')=='REAL_MEASUREMENT' and d.get('result')=='PASS': real.append(d.get('procedure'))
required=set(p.get('required_evidence',[])); status='BENCH_VERIFIED' if required and required.issubset(real) else p.get('status')
if status=='BENCH_VERIFIED' and not required.issubset(real): status='BENCH_PARTIAL'
Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps({'fixture_id':p['fixture_id'],'reported_status':status,'real_evidence_procedures':real,'synthetic_excluded':True},indent=2)+'\n')
