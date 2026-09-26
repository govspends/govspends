#!/usr/bin/env python3
"""Re-run each investigation's data checks (the scripts listed under `checks`) and fail if any tracked data file changes
as a result, which would mean the published tables no longer match what the scripts produce."""
import os, sys, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from registry import Registry, find_root
R=Registry(find_root()); fail=False
for inv in R.investigations:
    d=inv['inv_dir']
    for c in inv.get('checks',[]):
        print(f'== {inv["path"]}: {c}',flush=True); r=subprocess.run([sys.executable,c],cwd=d)
        if r.returncode: print('::error::check failed:',c); fail=True
    r=subprocess.run(['git','-C',d,'diff','--exit-code','--stat','--','data'])
    if r.returncode: print(f'::error::data files under {inv["path"]}/data changed when the scripts were re-run'); fail=True
sys.exit(1 if fail else 0)
