from ssd_sim.cli import main
def test_campaign(tmp_path):
    out=tmp_path/'t.json'; assert main(['campaign','--profile','simulator/ssd/profiles/synthetic_1g.yaml','--seed','1','--operations','3','--out',str(out)])==0; assert main(['inspect',str(out)])==0
