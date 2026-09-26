"""Registry access for the govspends tools.

Two kinds of repository use these tools:
  * the hub (governments.toml at the root): lists hub-owned jurisdictions (countries, states) and the government
    repositories; after tools/assemble.py has cloned them into build/repos/<path>, their jurisdiction.toml files
    are merged into one registry and the site is composed in build/docs;
  * a government repository (jurisdiction.toml at the root): one government, its profile page docs/index.md, and per
    investigation docs/<name>/ (pages) and investigations/<name>/ (evidence).
The root is taken from --root <dir>, else $GOVSPENDS_ROOT, else the current directory if it holds one of the two
files, else the hub that contains this tools/ folder.
"""
import os, re, sys, tomllib
TOOLS=os.path.dirname(os.path.abspath(__file__)); HUB=os.path.dirname(TOOLS)
LEVEL_TITLES={'national':'National government','state':'State government','counties':'Counties','cities':'Cities','districts':'Special districts'}
def find_root(argv=None):
    argv=argv or sys.argv
    if '--root' in argv: return os.path.abspath(argv[argv.index('--root')+1])
    if os.environ.get('GOVSPENDS_ROOT'): return os.path.abspath(os.environ['GOVSPENDS_ROOT'])
    cwd=os.getcwd()
    if os.path.exists(f'{cwd}/jurisdiction.toml') or os.path.exists(f'{cwd}/governments.toml'): return cwd
    return HUB
def parent_of(path):
    """Parent jurisdiction of a path: us/tx/counties/harris -> us/tx ; us/tx/state -> us/tx ; us/national -> us ; us/tx -> us."""
    parts=path.split('/')
    if len(parts)==1: return None
    if parts[-1] in ('state','national') or len(parts)==2: return '/'.join(parts[:-1])
    return '/'.join(parts[:-2])
def _toml(p): return tomllib.load(open(p,'rb'))
class Registry:
    def __init__(self,root=None,quiet=False):
        self.root=root or find_root(); self.quiet=quiet
        self.mode='government' if os.path.exists(f'{self.root}/jurisdiction.toml') else 'hub'
        self.jurisdictions={}; self.investigations=[]; self.governments=[]
        if self.mode=='hub':
            g=_toml(f'{self.root}/governments.toml')
            for k,v in g.get('jurisdiction',{}).items(): self.jurisdictions[k]={**v,'owner':'hub'}
            for gov in g.get('government',[]):
                gov=dict(gov); gov.setdefault('ref','main'); self.governments.append(gov)
                jt_path=f'{self.root}/build/repos/{gov["path"]}/jurisdiction.toml'
                if not os.path.exists(jt_path):
                    if not quiet: print(f'note: {gov["path"]} not fetched yet (run tools/assemble.py)',file=sys.stderr)
                    continue
                self._add_government(_toml(jt_path),gov['path'],gov['repo'],gov['ref'],f'{self.root}/build/repos/{gov["path"]}',f'{self.root}/build/docs/{gov["path"]}')
            self.docs_root=f'{self.root}/build/docs'
        else:
            jt=_toml(f'{self.root}/jurisdiction.toml')
            self._add_government(jt,jt['path'],jt.get('repo',''),jt.get('ref','main'),self.root,f'{self.root}/docs')
            self.docs_root=f'{self.root}/docs'
    def _add_government(self,jt,path,repo,ref,repo_dir,docs_dir):
        j={k:v for k,v in jt.items() if k!='investigation'}; j.update({'owner':'government','repo':repo,'ref':ref,'repo_dir':repo_dir,'docs_dir':docs_dir})
        self.jurisdictions[path]=j
        for inv in jt.get('investigation',[]):
            inv=dict(inv); rel=inv['path']
            inv.update({'rel':rel,'path':f'{path}/{rel}','gov':path,'docs':f'{docs_dir}/{rel}','inv_dir':f'{repo_dir}/investigations/{rel}','repo':repo,'ref':ref})
            self.investigations.append(inv)
    def name_of(self,path):
        if path in self.jurisdictions: return self.jurisdictions[path]['name']
        return LEVEL_TITLES.get(path.split('/')[-1],path.split('/')[-1])
    def gov_index_page(self,path):
        j=self.jurisdictions[path]
        return f'{j["docs_dir"]}/index.md' if j.get('owner')=='government' else f'{self.docs_root}/{path}/index.md'
    def site_url(self):
        m=re.search(r'^site_url:\s*(\S+)',open(f'{HUB}/mkdocs.yml').read(),re.M); return m.group(1).rstrip('/') if m else ''
    def repo_url(self):
        m=re.search(r'^repo_url:\s*(\S+)',open(f'{HUB}/mkdocs.yml').read(),re.M); return m.group(1).rstrip('/') if m else ''
def page_title(path):
    """Front-matter title if present, else the first H1, else the file name."""
    s=open(path).read()
    m=re.match(r'---\n(.*?)\n---',s,re.S)
    if m:
        t=re.search(r'^title:\s*"?(.*?)"?\s*$',m.group(1),re.M)
        if t: return t.group(1)
    m=re.search(r'^# (.+)$',s,re.M)
    return m.group(1).strip() if m else os.path.basename(path)
def _natural(s): return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)',s)]
def report_pages(inv):
    """The report's own pages in reading order: index, numbered sections, appendices."""
    d=inv['docs']; files=[f for f in os.listdir(d) if f.endswith('.md')]
    num=sorted([f for f in files if re.match(r'^\d{2}[a-z]?-',f)],key=_natural)
    app=sorted(f for f in files if f.startswith('appendix-'))
    return (['index.md'] if 'index.md' in files else [])+num+app
def extra_pages(inv):
    d=inv['docs']; out=[f for f in ('references.md','sources.md','audit-summary.md','independent-review.md') if os.path.exists(f'{d}/{f}')]
    notes=sorted(f'notes/{f}' for f in os.listdir(f'{d}/notes') if f.endswith('.md')) if os.path.isdir(f'{d}/notes') else []
    return out,notes
def nav_title(inv,rel):
    t=inv.get('nav_titles',{}).get(rel)
    return t if t else page_title(f'{inv["docs"]}/{rel}')
