"""MkDocs hook (declared in mkdocs.yml): pages imported from a government repository get edit and view links that
point at that repository instead of the hub. The mapping is written by tools/assemble.py into build/edit_urls.json."""
import json, os
_map=None
def on_page_context(context, page, config, nav):
    global _map
    if _map is None:
        p=os.path.join(os.path.dirname(config['config_file_path']),'edit_urls.json')
        _map=json.load(open(p)) if os.path.exists(p) else {}
    src=page.file.src_uri
    for prefix,base in sorted(_map.items(),key=lambda kv:-len(kv[0])):
        if src.startswith(prefix+'/'):
            page.edit_url=base+src[len(prefix)+1:]; break
    return context
