#!/usr/bin/env python3
"""Build each report's PDF from its Markdown pages (the pages are the source of truth).

Concatenates the report pages in reading order, converts them with Python-Markdown and renders with WeasyPrint using a
print stylesheet that mirrors the site (letter size, running footer with page numbers, each section on a new page,
zebra tables, small grey captions). Output: <pages folder>/<report_pdf> for every investigation in the registry
(ignored by git; built in CI and published with the site). Optional argument: one investigation path.
"""
import os, re, sys, datetime
import markdown
from weasyprint import HTML
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from registry import Registry, find_root, report_pages
R=Registry(find_root())
CSS='''
@page { size: letter; margin: 0.75in 0.8in 0.8in 0.8in;
  @bottom-left { content: "__TITLE__  |  __SITE__  |  built __DATE__ from the website pages"; font: 7.5pt Helvetica, Arial, sans-serif; color: #52514e; }
  @bottom-right { content: "Page " counter(page); font: 7.5pt Helvetica, Arial, sans-serif; color: #52514e; } }
body { font: 9.6pt/1.35 Helvetica, Arial, "Liberation Sans", sans-serif; color: #0b0b0b; }
h1 { font-size: 16pt; margin: 0 0 8pt; page-break-before: always; page-break-after: avoid; }
h1.first { page-break-before: auto; font-size: 24pt; line-height: 1.15; }
h2 { font-size: 12pt; margin: 10pt 0 5pt; page-break-after: avoid; }
p { margin: 0 0 5pt; } li { margin: 0 0 3pt; } ul { padding-left: 14pt; }
p.kicker { font-size: 13pt; color: #52514e; margin-bottom: 2pt; } p.lead { font-size: 11.5pt; line-height: 1.3; margin: 8pt 0; }
p.caption { font-size: 8pt; line-height: 1.25; color: #52514e; margin: 1pt 0 8pt; }
img { max-width: 100%; height: auto; display: block; margin: 4pt auto 2pt; page-break-inside: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 8.2pt; line-height: 1.2; margin: 4pt 0 2pt; page-break-inside: auto; }
th { text-align: left; font-weight: bold; border-bottom: 0.6pt solid #0b0b0b; padding: 2.5pt 3pt; vertical-align: top; }
td { padding: 2.5pt 3pt; vertical-align: top; } tr:nth-child(even) td { background: #f3f2ef; }
tbody tr:last-child td { border-bottom: 0.4pt solid #b9b8b2; } thead { display: table-header-group; }
td[align=right], th[align=right] { text-align: right; }
code { font: 8pt "Liberation Mono", monospace; }
'''.replace('__DATE__',datetime.date.today().isoformat())
def build(inv):
    DOCS=inv['docs']; out=f'{DOCS}/{inv["report_pdf"]}'
    site=(R.site_url().replace('https://','')+'/'+inv['path']+'/') if R.site_url() else inv['path']
    css=CSS.replace('__TITLE__',inv['title'].replace('"','')).replace('__SITE__',site)
    parts=[]
    for i,f in enumerate(report_pages(inv)):
        md=open(f'{DOCS}/{f}').read()
        md=re.sub(r'^---\n.*?\n---\n','',md,flags=re.S)                  # front matter
        md=re.sub(r'<!-- generated:[^\n]*-->\n?','',md)
        md=re.sub(r'!!! \w+ "[^"]*"\n(    .*\n?)+','',md)                  # admonitions are site-only
        html=markdown.markdown(md,extensions=['tables','attr_list','md_in_html','sane_lists'])
        if i==0: html=html.replace('<h1>','<h1 class="first">',1)
        parts.append(html)
    doc=f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(parts)}</body></html>'
    HTML(string=doc,base_url=DOCS+'/').write_pdf(out)
    print('wrote',out,os.path.getsize(out),'bytes')
sel=[a for a in sys.argv[1:] if not a.startswith('--') and a!=find_root()]
for inv in R.investigations:
    if inv.get('report_pdf') and (not sel or inv['path'] in sel or inv['rel'] in sel): build(inv)
