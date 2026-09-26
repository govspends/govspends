#!/usr/bin/env python3
"""Report builder -> Markdown.

The investigation's scripts/build_report.py describes the report as reportlab flowables. This module executes it with
the reportlab classes replaced by recorders and renders the recorded content as Markdown. It is used in two ways:
  * one-time conversion (python3 tools/export_markdown.py): writes one page per top-level section into docs/;
    after that the Markdown pages are the source of truth for the report text;
  * by tools/build_tables.py, which re-renders only the tables that are computed from data files (they sit between
    <!-- generated:<key> start/end --> markers in the pages) so that data changes flow into the site.
"""
import re, sys, types, os, glob, shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))

# ---- recorders standing in for reportlab -------------------------------------------------------
class Style:
    def __init__(self,name,parent=None,**kw): self.name=name; self.parent=parent
class Paragraph:
    def __init__(self,text,style=None,bulletText=None): self.text=text; self.style=style; self.bullet=bulletText
class Spacer:
    def __init__(self,*a,**k): pass
class PageBreak:
    def __init__(self,*a,**k): pass
class KeepTogether:
    def __init__(self,items): self.items=items
class Image:
    def __init__(self,path,width=None,height=None): self.path=path; self.width=width
class Table:
    def __init__(self,rows,colWidths=None,repeatRows=0,style=None): self.rows=rows
    def setStyle(self,st): pass
class TableStyle:
    def __init__(self,*a,**k): pass
_captured=[]
class Doc:
    def __init__(self,*a,**k): pass
    def build(self,S,onFirstPage=None,onLaterPages=None): _captured.append(list(S))
class _Colors:
    def HexColor(self,x): return x
class _ImageReader:
    def __init__(self,path): self.path=path
    def getSize(self): return (10,6)
def _fake(name,**attrs):
    m=types.ModuleType(name); m.__dict__.update(attrs); sys.modules[name]=m; return m
def install_recorders():
    _fake('reportlab'); _fake('reportlab.lib',colors=_Colors()); _fake('reportlab.lib.pagesizes',letter=(612,792)); _fake('reportlab.lib.units',inch=72)
    _fake('reportlab.lib.colors',HexColor=lambda x:x)
    _fake('reportlab.lib.styles',getSampleStyleSheet=lambda:{'Heading1':Style('Heading1'),'Heading2':Style('Heading2'),'Normal':Style('Normal')},ParagraphStyle=Style)
    _fake('reportlab.platypus',SimpleDocTemplate=Doc,Paragraph=Paragraph,Spacer=Spacer,Image=Image,Table=Table,TableStyle=TableStyle,PageBreak=PageBreak,KeepTogether=KeepTogether)
    _fake('reportlab.lib.enums',TA_LEFT=0); _fake('reportlab.lib.utils',ImageReader=_ImageReader)

def run_report(inv,script='scripts/build_report.py'):
    """Execute the investigation's report builder against the recorders; return the flat list of flowables."""
    install_recorders(); _captured.clear()
    src=open(f'{inv}/{script}').read()
    src=re.sub(r"^B=[^;\n]*",f"B='{inv}'",src,count=1,flags=re.M)   # keep anything after ';' on that line
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):          # the builder prints 'wrote <pdf>'; nothing is written in recorder mode
        exec(compile(src,'build_report.py','exec'),{'__name__':'__report__','__file__':f'{inv}/scripts/build_report.py'})
    flat=[]
    for e in _captured[-1]:
        flat+= e.items if isinstance(e,KeepTogether) else [e]
    return flat

# ---- markup helpers ------------------------------------------------------------------------------
def md_inline(t):
    t=t.replace('&amp;','&').replace('<br/>',' ').replace('<br>',' ')
    t=re.sub(r'<b>(\s*)(.*?)(\s*)</b>',r'\1**\2**\3',t,flags=re.S)
    t=re.sub(r'<i>(\s*)(.*?)(\s*)</i>',r'\1*\2*\3',t,flags=re.S)
    return re.sub(r'[ \t]+',' ',t).strip()
def html_inline(t):
    t=t.replace('<br/>',' ')
    t=re.sub(r'<b>(.*?)</b>',r'<strong>\1</strong>',t,flags=re.S); t=re.sub(r'<i>(.*?)</i>',r'<em>\1</em>',t,flags=re.S)
    return t.strip()
def cell(c):
    if isinstance(c,Paragraph): c=c.text
    return md_inline(str(c)).replace('|','\\|').replace('\n',' ')
def numeric(s):
    s=re.sub(r'[\$,%()+\-\s*]','',s); return bool(s) and bool(re.fullmatch(r'[\d.]+M?|n/a',s))
GENERATED={'Table 1.':'table1_measures','Table 2b.':'table2b_growth_bridge','Table 8 (left).':'table8_grades_and_examples',
           'Table 10.':'table10_labor_by_department','Table 12.':'table12_city_vs_county','Sources: FY27 Vol. I v3 Appendix A (FY25 actual':'appendix_a_departments'}
def table_md(t):
    rows=t.rows
    if rows and any(isinstance(c,Table) for c in rows[0]):
        return '\n\n'.join(table_md(c) for r in rows for c in r if isinstance(c,Table))
    cells=[[cell(c) for c in r] for r in rows]
    ncol=max(len(r) for r in cells)
    for r in cells: r+=['']*(ncol-len(r))
    align=[]
    for j in range(ncol):
        body=[r[j] for r in cells[1:] if r[j]]
        align.append('---:' if body and sum(numeric(x) for x in body)/len(body)>0.7 else '---')
    out=['| '+' | '.join(cells[0])+' |','| '+' | '.join(align)+' |']+['| '+' | '.join(r)+' |' for r in cells[1:]]
    return '\n'.join(out)
def generated_key(e,nxt):
    if isinstance(e,Table) and isinstance(nxt,Paragraph) and nxt.style and nxt.style.name in ('CAP','SM'):
        for pre,k in GENERATED.items():
            if nxt.text.startswith(pre): return k
    return None
def wrap_generated(key,md):
    return f'<!-- generated:{key} start (built from the data files by tools/build_tables.py; change the data, not this table) -->\n{md}\n<!-- generated:{key} end -->'

SLUGS=[('1.','index.md'),('2.','02-budget-size.md'),('3.','03-shortfall.md'),('4.','04-tax-rate.md'),('5.','05-where-the-money-goes.md'),
       ('6.','06-pay-increases.md'),('6A.','06a-salary-detail.md'),('6B.','06b-health-benefits.md'),('6C.','06c-city-vs-county-pay.md'),
       ('7.','07-transparency.md'),('8.','08-timeline.md'),('Appendix A.','appendix-a-departments.md'),('Appendix B.','appendix-b-method.md')]
def slug_for(h):
    for pre,f in SLUGS:
        if h.startswith(pre): return f
    raise SystemExit('no slug for heading '+h)

def render_pages(flat):
    pages={}; cur='index.md'; buf=pages.setdefault(cur,[])
    for i,e in enumerate(flat):
        nxt=flat[i+1] if i+1<len(flat) else None
        if isinstance(e,Paragraph):
            st=e.style.name if e.style else 'P'; t=e.text
            if st=='H1':
                cur=slug_for(md_inline(t)); buf=pages.setdefault(cur,[])
                buf.append(('## ' if cur=='index.md' else '# ')+md_inline(t)+'\n')
            elif st=='H2': buf.append('## '+md_inline(t).rstrip('.')+'\n')
            elif st=='t0': buf.append('<p class="kicker">'+html_inline(t)+'</p>\n')
            elif st=='t1': buf.append('# '+md_inline(t)+'\n')
            elif st=='t2': buf.append('<p class="lead">'+html_inline(t)+'</p>\n')
            elif st in ('CAP','SM'): buf.append('<p class="caption">'+html_inline(t)+'</p>\n')
            elif e.bullet: buf.append('- '+md_inline(t)+'\n')
            else: buf.append(md_inline(t)+'\n')
        elif isinstance(e,Image):
            name=os.path.basename(e.path); buf.append(f'![{name.split(".")[0]}](charts/{name})\n')
        elif isinstance(e,Table):
            key=generated_key(e,nxt); md=table_md(e)
            buf.append((wrap_generated(key,md) if key else md)+'\n')
    return {f:re.sub(r'\n{3,}','\n\n','\n'.join(parts)).rstrip()+'\n' for f,parts in pages.items()}

def generated_tables(flat):
    out={}
    for i,e in enumerate(flat):
        k=generated_key(e,flat[i+1] if i+1<len(flat) else None)
        if k: out[k]=table_md(e)
    return out

def copy_charts(inv,docs):
    os.makedirs(f'{docs}/charts',exist_ok=True); n=0
    for c in glob.glob(f'{inv}/charts/*.png'):
        shutil.copy(c,f'{docs}/charts/'); n+=1
    return n

if __name__=='__main__':
    from registry import Registry, find_root
    R=Registry(find_root()); cands=[i for i in R.investigations if i.get('tables_from')]
    sel=[a for a in sys.argv[1:] if not a.startswith('--')]
    if sel: cands=[i for i in cands if i['path'] in sel or i['rel'] in sel]
    if not cands: raise SystemExit('no investigation with tables_from selected')
    inv=cands[0]; INV,DOCS=inv['inv_dir'],inv['docs']
    flat=run_report(INV,inv['tables_from']); pages=render_pages(flat); os.makedirs(DOCS,exist_ok=True)
    for f,text in pages.items():
        open(f'{DOCS}/{f}','w').write(text); print(f'{f:32s} {len(text):7d} chars')
    print('charts copied:',copy_charts(INV,DOCS))
