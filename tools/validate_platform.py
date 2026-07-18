#!/usr/bin/env python3
import argparse, sys, yaml
STATUSES={'DESIGN_DRAFT','DESIGN_RULES_PASSED','ASSEMBLED_UNVERIFIED','BENCH_PARTIAL','BENCH_VERIFIED','REJECTED'}
def main():
 p=argparse.ArgumentParser(); p.add_argument('platform'); p.add_argument('--strict',action='store_true'); a=p.parse_args(); d=yaml.safe_load(open(a.platform))
 errs=[]
 for k in ['fixture_id','board_revision','status','nand','power','interface','allowed_nand_ranges','evidence_status']: 
  if k not in d: errs.append(f'missing {k}')
 if d.get('status') not in STATUSES: errs.append('bad status')
 nand_v=float(d.get('nand',{}).get('io_voltage_v',0)); host_v=float(d.get('power',{}).get('host_io_voltage_v',0)); iface=d.get('interface',{})
 if host_v>nand_v+0.3 and not (iface.get('level_shifter') and iface.get('validated_logic_thresholds')): errs.append('unsafe 3.3V host to 1.8V NAND without validated interface')
 for r in d.get('allowed_nand_ranges',[]):
  if r['first_block']<0 or r['last_block']<r['first_block']: errs.append('bad range')
 if d.get('status')=='BENCH_VERIFIED': errs.append('BENCH_VERIFIED requires evidence validator promotion, not platform-only validation')
 if errs: print('\n'.join(errs)); return 1
 print('platform validation passed')
 return 0
if __name__=='__main__': sys.exit(main())
