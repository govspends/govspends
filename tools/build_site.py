#!/usr/bin/env python3
"""Generate what follows from the registries.

Hub (after tools/assemble.py):  the navigation (build/mkdocs.yml), the investigations table on the landing page and
the generated block of every jurisdiction page, all in build/docs (nothing committed changes).
Government repository:          the generated block of docs/index.md (facts and the list of investigations).
--check exits 1 if anything would change (used in government repositories' CI).
"""
import os, re, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from registry import Registry, find_root, HUB, LEVEL_TITLES, report_pages, extra_pages, nav_title, parent_of
R=Registry(find_root()); check='--check' in sys.argv; changed=[]
def write(path,text):
    old=open(path).read() if os.path.exists(path) else None
    if old!=text:
        changed.append(os.path.relpath(path,R.root))
        if not check: os.makedirs(os.path.dirname(path),exist_ok=True); open(path,'w').write(text)
def q(s): return '"'+s.replace('\\','\\\\').replace('"','\\"')+'"'
def rel(frm,to): return os.path.relpath(to,frm).replace(os.sep,'/')
def inv_table(invs,here):
    L=['| Investigation | Status | Headline |','|---|---|---|']
    for i in sorted(invs,key=lambda i:i['path']): L.append(f'| [{i["title"]}]({rel(here,f"{i["docs"]}/index.md")}) | {i["status"]} | {i["headline"]} |')
    return L
def facts_block(path,here):
    j=R.jurisdictions.get(path,{}); facts=[]
    if j.get('type'): facts.append(('Level',j['type']))
    if R.mode=='hub':
        p=parent_of(path)
        if p and p in R.jurisdictions: facts.append(('Part of',f'[{R.name_of(p)}]({rel(here,f"{R.docs_root}/{p}/index.md")})'))
    else:
        hub=j.get('hub','').rstrip('/'); parts=path.split('/'); links=[]
        if j.get('state') and len(parts)>2: links.append(f'[{j["state"]}]({hub}/{parts[0]}/{parts[1]}/)')
        if j.get('country'): links.append(f'[{j["country"]}]({hub}/{parts[0]}/)')
        if links: facts.append(('Part of',', '.join(links)))
    for k,lab in (('seat','Seat'),('governing_body','Governing body'),('fiscal_year','Fiscal year')):
        if j.get(k): facts.append((lab,j[k]))
    if j.get('websites'): facts.append(('Official websites',', '.join(f'<{w}>' for w in j['websites'])))
    if j.get('repo'): facts.append(('Repository',f'<{j["repo"]}>'))
    return ['| | |','|---|---|']+[f'| **{a}** | {b} |' for a,b in facts]+[''] if facts else []
def splice(page,default_title,block):
    s=open(page).read() if os.path.exists(page) else f'# {default_title}\n\n<!-- generated:jurisdiction start -->\n<!-- generated:jurisdiction end -->\n\n_Add a short description of this government here (how it is governed, its fiscal year, where its budget documents are published)._\n'
    if '<!-- generated:jurisdiction start -->' not in s: s=s.rstrip()+'\n\n<!-- generated:jurisdiction start -->\n<!-- generated:jurisdiction end -->\n'
    write(page,re.sub(r'<!-- generated:jurisdiction start -->.*?<!-- generated:jurisdiction end -->','<!-- generated:jurisdiction start -->\n'+block.rstrip()+'\n<!-- generated:jurisdiction end -->',s,flags=re.S))
if R.mode=='government':
    path=next(iter(R.jurisdictions)); page=f'{R.root}/docs/index.md'; here=os.path.dirname(page)
    L=facts_block(path,here)
    L+=['**Investigations**','']+inv_table(R.investigations,here)+[''] if R.investigations else ['_No investigation published yet for this government._','']
    splice(page,f'{R.name_of(path)}','\n'.join(L))
else:
    nodes={}
    for k in list(R.jurisdictions)+[i['gov'] for i in R.investigations]:
        parts=k.split('/')
        for n in range(1,len(parts)+1): nodes.setdefault('/'.join(parts[:n]),set())
    for k in nodes:
        if '/' in k: nodes[os.path.dirname(k)].add(k)
    def sort_key(p): return (0 if p.split('/')[-1] in ('national','state') else 1, R.name_of(p).lower())
    def inv_nav(inv,ind):
        L=[f'{ind}- {q(inv["short_title"])}:']
        for f in report_pages(inv): L.append(f'{ind}    - {q(nav_title(inv,f))}: {inv["path"]}/{f}')
        extras,notes=extra_pages(inv)
        for f in extras: L.append(f'{ind}    - {q(nav_title(inv,f))}: {inv["path"]}/{f}')
        if notes:
            L.append(f'{ind}    - Notes:')
            for f in notes: L.append(f'{ind}        - {q(nav_title(inv,f))}: {inv["path"]}/{f}')
        return L
    def node_nav(path,ind):
        L=[f'{ind}- {q(R.name_of(path))}:']
        if os.path.exists(f'{R.docs_root}/{path}/index.md'): L.append(f'{ind}    - {path}/index.md')
        for c in sorted(nodes[path],key=sort_key): L+=node_nav(c,ind+'    ')
        for inv in sorted([i for i in R.investigations if i['gov']==path],key=lambda i:i['path']): L+=inv_nav(inv,ind+'    ')
        return L
    nav=['nav:','  - Home: index.md','  - How govspends is organized: about/structure.md','  - How to contribute: contributing.md']
    for top in sorted([p for p in nodes if '/' not in p],key=lambda p:R.name_of(p)): nav+=node_nav(top,'  ')
    cfg=open(f'{HUB}/mkdocs.yml').read()
    cfg=re.sub(r'# nav-start.*?# nav-end','# nav-start (generated by tools/assemble.py; edit governments.toml and the repositories, not this file)\n'+'\n'.join(nav)+'\n# nav-end',cfg,flags=re.S)
    cfg=cfg.replace('hooks: [tools/mkdocs_hooks.py]','hooks: [../tools/mkdocs_hooks.py]')
    write(f'{R.root}/build/mkdocs.yml',cfg)
    # landing table
    rows=['| Investigation | Government | Status | Headline |','|---|---|---|---|']
    for inv in sorted(R.investigations,key=lambda i:i['path']):
        rows.append(f'| [{inv["title"]}]({inv["path"]}/index.md) | [{R.name_of(inv["gov"])}]({inv["gov"]}/index.md) | {inv["status"]} | {inv["headline"]} |')
    s=open(f'{R.docs_root}/index.md').read()
    write(f'{R.docs_root}/index.md',re.sub(r'<!-- generated:investigations start -->.*?<!-- generated:investigations end -->','<!-- generated:investigations start -->\n'+'\n'.join(rows)+'\n<!-- generated:investigations end -->',s,flags=re.S))
    # jurisdiction pages
    for path in R.jurisdictions:
        page=f'{R.docs_root}/{path}/index.md'; here=os.path.dirname(page); L=facts_block(path,here)
        kids=[]
        for c in sorted(nodes.get(path,()),key=sort_key):
            if c in R.jurisdictions: kids.append(c)
            else: kids+=sorted([g for g in nodes.get(c,()) if g in R.jurisdictions],key=sort_key)
        if kids: L+=['**Governments covered**','']+[f'- [{R.name_of(c)}]({rel(here,f"{R.docs_root}/{c}/index.md")}) ({R.jurisdictions[c].get("type","")}; {len([i for i in R.investigations if i["gov"]==c or i["gov"].startswith(c+"/")])} investigation(s))' for c in kids]+['']
        mine=[i for i in R.investigations if i['gov']==path or i['gov'].startswith(path+'/')]
        L+=['**Investigations**','']+inv_table(mine,here)+[''] if mine else ['_No investigation published yet for this government._','']
        if not os.path.exists(page): print(f'note: {path} has no page in docs/; a placeholder was generated. Add docs/{path}/index.md to the hub.',file=sys.stderr)
        splice(page,R.name_of(path),'\n'.join(L))
if check and changed: print('OUT OF DATE (run python3 tools/build_site.py):',', '.join(changed)); sys.exit(1)
print(('generated pages rebuilt: ' if changed else 'generated pages already current ')+', '.join(changed))
