"""Create a public source tree using an explicit allowlist; never copy runtime data."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROOT_FILES=['README.md','README.fa.md','LICENSE','CHANGELOG.md','CONTRIBUTING.md','SECURITY.md','.gitignore','.env.example','package.json','package-lock.json','server.js','client.js','domain-client.js','env.js','cli.js','raw-cli.js','cli-http-map.js','shortcuts.js','transactions.js','transfer.js','transfer-input.js','transfer-modes.js','transfer-schema.js','build-api-docs.js','build-catalog.py','local-openapi.json','local-postman_collection.json','openapi.json','parsian-api.postman_collection.json','API-REFERENCE.fa.md','CLI-REFERENCE.fa.md','TRANSFER-GUIDE.fa.md','TRANSFERS-FIXED.fa.md','TRANSFERS-SMS.fa.md','python/pyproject.toml','python/README.md','python/CHANGELOG.md','python/LICENSE','python/.gitignore','data/endpoints.json','data/cli-http-map.json']
TREES=['test','docs','.github','scripts','assets','python/src','python/tests','python/tools','python/docs','python/examples']
PRIVATE_KEYS={'sessionid','authorization','password','signedpassword','secondpassword','pin','pan','destinationpan','sourcedepositnumber','accountnumber','depositnumber','iban','ibannumber','mobileno','mobilenumber','username','customerno','customernumber','cif','workflowinstanceid','instanceid'}

def secret_values(captures:list[str])->set[str]:
    found:set[str]=set()
    def visit(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key.lower() in PRIVATE_KEYS and isinstance(item,(str,int)) and len(str(item))>=7:found.add(str(item))
                visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    for filename in captures:
        har=json.loads(Path(filename).read_text(encoding='utf-8-sig'))
        for entry in har.get('log',{}).get('entries',[]):
            for header in entry.get('request',{}).get('headers',[]):
                if header.get('name','').lower() in PRIVATE_KEYS and len(header.get('value',''))>=7:found.add(header['value'])
            for content in [entry.get('request',{}).get('postData',{}),entry.get('response',{}).get('content',{})]:
                text=content.get('text','')
                if content.get('encoding')=='base64':text=base64.b64decode(text).decode('utf8',errors='replace')
                try:visit(json.loads(text))
                except (ValueError,TypeError):pass
    return found

def prepare(captures:list[str])->Path:
    destination=ROOT/'release'/'parsian-api'
    destination.mkdir(parents=True,exist_ok=True)
    paths={Path(name) for name in ROOT_FILES}
    for tree in TREES:
        base=ROOT/tree
        if base.exists():
            paths.update(p.relative_to(ROOT) for p in base.rglob('*') if p.is_file() and not any(part in {'__pycache__','.pytest_cache','.venv','node_modules'} for part in p.parts) and p.suffix not in {'.pyc','.pyo'})
    secrets=secret_values(captures)
    for relative in sorted(paths):
        source=ROOT/relative
        if not source.is_file():raise RuntimeError('Required publication file missing: '+str(relative))
        if not source.resolve().is_relative_to(ROOT):raise RuntimeError('Publication source escaped project root')
        if source.name=='.env' or 'session.json'==source.name or source.suffix=='.har':raise RuntimeError('Private file rejected')
        data=source.read_bytes()
        try:text=data.decode('utf8')
        except UnicodeDecodeError:text=''
        if re.search(r'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}',text):raise RuntimeError('Token-shaped text rejected in '+str(relative))
        workstation_pattern = r'(?:[A-Z]:[\\/](?:Users|bluapi)|/' + r'Users/[^/]+/)'
        if re.search(workstation_pattern,text):raise RuntimeError('Workstation path rejected in '+str(relative))
        for secret in secrets:
            if re.search(r'(?<!\w)'+re.escape(secret)+r'(?!\w)',text):raise RuntimeError('Captured private value rejected in '+str(relative))
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    actual={p.relative_to(destination) for p in destination.rglob('*') if p.is_file() and '.git' not in p.relative_to(destination).parts}
    if actual!=paths:raise RuntimeError('Unexpected existing files in publication directory; inspect manually')
    manifest={str(p).replace('\\','/'):hashlib.sha256((destination/p).read_bytes()).hexdigest() for p in sorted(paths)}
    (ROOT/'release'/'SOURCE-SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=ROOT/'release'/'parsian-api-source.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for relative in sorted(paths):z.write(destination/relative,arcname='parsian-api/'+str(relative).replace('\\','/'))
    artifacts=ROOT/'release'/'python-dist';artifacts.mkdir(exist_ok=True)
    for file in (ROOT/'python/dist').glob('*'):
        if file.suffix=='.whl' or file.name.endswith('.tar.gz'):shutil.copyfile(file,artifacts/file.name)
    print(json.dumps({'source_files':len(paths),'source_tree':str(destination),'source_zip':str(archive),'captured_values_checked':len(secrets)}))
    return destination

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--capture',action='append',default=[])
    prepare(parser.parse_args().capture)
