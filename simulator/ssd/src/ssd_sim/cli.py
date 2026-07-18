import argparse,json,sys
from .profiles import load_profile, verify_profile
from .nand import Nand
def main(argv=None):
 p=argparse.ArgumentParser(prog='ssd-sim'); sub=p.add_subparsers(dest='cmd',required=True)
 for c in ['run','campaign']: sub.add_parser(c).add_argument('--profile',required=True); sub.choices[c].add_argument('--seed',type=int,default=1); sub.choices[c].add_argument('--operations',type=int,default=10); sub.choices[c].add_argument('--out',default='artifacts/ssd-sim-trace.json')
 sub.add_parser('verify-profile').add_argument('profile')
 sub.add_parser('replay').add_argument('trace')
 sub.add_parser('inspect').add_argument('trace')
 a=p.parse_args(argv)
 if a.cmd=='verify-profile': print(verify_profile(a.profile)); return 0
 if a.cmd in ('run','campaign'):
  d,g,h=load_profile(a.profile); n=Nand(g,h,a.seed)
  for i in range(a.operations): n.wen(); n.program(i%g.page_count, bytes([i&255])*g.page_size)
  n.trace.save(a.out); open(a.out+'.metrics','w').write(json.dumps(n.metrics(),sort_keys=True)+'\n'); print(a.out); return 0
 events=json.load(open(a.trace)); print(json.dumps({'events':len(events),'final_sequence':events[-1]['sequence'] if events else 0},sort_keys=True)); return 0
if __name__=='__main__': sys.exit(main())
