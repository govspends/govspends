#!/usr/bin/env python3
"""Refresh the data-driven tables and chart images in the report pages of every investigation that declares
`tables_from` (a reportlab report builder) in its jurisdiction.toml.

Those tables sit between <!-- generated:<key> start --> / <!-- generated:<key> end --> markers in the pages; the
script rebuilds them from the data by running the builder with recording stand-ins for reportlab, splices them in,
and copies the chart images into the pages folder.   --check exits 1 if any page or chart would change.
"""
import re, sys, os, glob, filecmp, shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from registry import Registry, find_root
from export_markdown import run_report, generated_tables, wrap_generated
R=Registry(find_root()); check='--check' in sys.argv; changed=[]
for inv in R.investigations:
    if not inv.get('tables_from'): continue
    INV,DOCS=inv['inv_dir'],inv['docs']
    tables=generated_tables(run_report(INV,inv['tables_from']))
    for page in sorted(glob.glob(f'{DOCS}/*.md')):
        s=open(page).read(); new=s
        for key,md in tables.items():
            pat=re.compile(r'<!-- generated:%s start[^\n]*-->\n.*?\n<!-- generated:%s end -->'%(re.escape(key),re.escape(key)),re.S)
            if pat.search(new): new=pat.sub(lambda m: wrap_generated(key,md),new)
        if new!=s:
            changed.append(f'{inv["path"]}/{os.path.basename(page)}')
            if not check: open(page,'w').write(new)
    for c in sorted(glob.glob(f'{INV}/charts/*.png')):
        d=f'{DOCS}/charts/{os.path.basename(c)}'
        if not os.path.exists(d) or not filecmp.cmp(c,d,shallow=False):
            changed.append(f'{inv["path"]}/charts/{os.path.basename(c)}')
            if not check: os.makedirs(os.path.dirname(d),exist_ok=True); shutil.copy(c,d)
if check and changed: print('OUT OF DATE (run build_tables):',', '.join(changed)); sys.exit(1)
print(('generated tables refreshed: ' if changed else 'generated tables already current ')+', '.join(changed))
