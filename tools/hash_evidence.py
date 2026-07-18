#!/usr/bin/env python3
import argparse, hashlib, pathlib
p=argparse.ArgumentParser(); p.add_argument('file'); a=p.parse_args(); print(hashlib.sha256(pathlib.Path(a.file).read_bytes()).hexdigest())
