#!/usr/bin/env python3
import argparse, hashlib, pathlib
ap=argparse.ArgumentParser(); ap.add_argument('profile'); ap.add_argument('--out',required=True); a=ap.parse_args(); raw=pathlib.Path(a.profile).read_bytes(); pathlib.Path(a.out).write_text('#define GENERATED_NAND_PROFILE_SHA256 "'+hashlib.sha256(raw).hexdigest()+'"\n')
