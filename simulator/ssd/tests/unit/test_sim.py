from ssd_sim.profiles import load_profile
from ssd_sim.nand import Nand
def test_program_read(tmp_path):
    _,g,h=load_profile('simulator/ssd/profiles/synthetic_1g.yaml'); n=Nand(g,h,1); n.wen(); assert n.program(0,b'\0'*g.page_size)=='OK'; data,status=n.read(0); assert status=='OK' and data[0]==0 and n.trace.events
