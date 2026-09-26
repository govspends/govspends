#!/usr/bin/env python3
"""Compose the website from the hub and the government repositories (hub only).

  1. clone (or refresh) every repository in governments.toml into build/repos/<path> (shallow, the listed branch);
     --local <path>=<dir> uses a local checkout instead (for previewing changes before they are pushed); a government
     repository cloned inside the hub folder under its GitHub name (us-tx-counties-harris/) is used automatically
     (--no-local forces clones)
  2. copy the hub's docs/ and CONTRIBUTING.md, then each government's docs/, into build/docs/<path>/
  3. write build/edit_urls.json so that edit links on imported pages open the government's repository
  4. run build_site.py: navigation into build/mkdocs.yml, landing table, jurisdiction pages
Then: python3 tools/build_pdf.py ; mkdocs build --strict -f build/mkdocs.yml   (or mkdocs serve -f build/mkdocs.yml)
"""
import os, sys, shutil, subprocess, json, re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from registry import Registry, find_root, HUB
root=find_root(); B=f'{root}/build'
assert os.path.exists(f'{root}/governments.toml'), 'assemble.py runs in the hub repository'
local={}
for i,a in enumerate(sys.argv):
    if a=='--local': p,d=sys.argv[i+1].split('=',1); local[p]=os.path.abspath(d)
R=Registry(root,quiet=True)
os.makedirs(f'{B}/repos',exist_ok=True)
for gov in R.governments:                      # a government repository cloned inside the hub folder (us-tx-counties-harris/) is used as is
    nested=f'{root}/{gov["path"].replace("/","-")}'
    if gov['path'] not in local and '--no-local' not in sys.argv and os.path.exists(f'{nested}/jurisdiction.toml'): local[gov['path']]=nested
for gov in R.governments:
    dest=f'{B}/repos/{gov["path"]}'
    if gov['path'] in local:
        if os.path.islink(dest) or os.path.exists(dest): (os.unlink if os.path.islink(dest) else shutil.rmtree)(dest)
        os.makedirs(os.path.dirname(dest),exist_ok=True); os.symlink(local[gov['path']],dest); print(f'{gov["path"]}: using local checkout {local[gov["path"]]}')
    elif os.path.islink(dest) or not os.path.exists(f'{dest}/.git'):
        if os.path.islink(dest): os.unlink(dest)
        shutil.rmtree(dest,ignore_errors=True); os.makedirs(os.path.dirname(dest),exist_ok=True)
        subprocess.run(['git','clone','-q','--depth','1','--branch',gov['ref'],gov['repo'],dest],check=True); print(f'{gov["path"]}: cloned {gov["repo"]}@{gov["ref"]}')
    else:
        subprocess.run(['git','-C',dest,'fetch','-q','--depth','1','origin',gov['ref']],check=True); subprocess.run(['git','-C',dest,'checkout','-q','FETCH_HEAD'],check=True); print(f'{gov["path"]}: refreshed')
R=Registry(root)                                   # now with the governments' jurisdiction.toml files
if os.path.exists(f'{B}/docs'): shutil.rmtree(f'{B}/docs')
shutil.copytree(f'{root}/docs',f'{B}/docs')
c=open(f'{root}/CONTRIBUTING.md').read().replace('(LICENSE)',f'({R.repo_url()}/blob/main/LICENSE)').replace('](docs/about/structure.md)','](about/structure.md)')
open(f'{B}/docs/contributing.md','w').write(c)
edit={}
for path,j in R.jurisdictions.items():
    if j.get('owner')!='government': continue
    src=f'{j["repo_dir"]}/docs'
    if os.path.exists(src): shutil.copytree(src,f'{B}/docs/{path}',dirs_exist_ok=True)
    edit[path]=f'{j["repo"]}/edit/{j["ref"]}/docs/'
json.dump(edit,open(f'{B}/edit_urls.json','w'),indent=1)
subprocess.run([sys.executable,f'{HUB}/tools/build_site.py','--root',root],check=True)
print('assembled: build/docs, build/mkdocs.yml, build/edit_urls.json')
