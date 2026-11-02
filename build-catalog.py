import json,pathlib,urllib.parse,re,sys,collections,hashlib
root=pathlib.Path(__file__).resolve().parent
if len(sys.argv) < 2:
    raise SystemExit('Usage: python build-catalog.py CAPTURE_FILE')
source=pathlib.Path(sys.argv[1])
sources=[pathlib.Path(p) for p in sys.argv[1:]] or [source]
har={'log':{'entries':[]}}
for capture in sources:har['log']['entries'].extend(json.loads(capture.read_text(encoding='utf-8-sig'))['log']['entries'])
def schema(v):
 if v is None:return {'nullable':True}
 if isinstance(v,dict):return {'type':'object','properties':{k:schema(x) for k,x in v.items()}}
 if isinstance(v,list):return {'type':'array','items':merge([schema(x) for x in v]) if v else {}}
 return {'type':'boolean' if isinstance(v,bool) else 'integer' if isinstance(v,int) else 'number' if isinstance(v,float) else 'string'}
def merge(values):
 unique=list({json.dumps(v,sort_keys=True):v for v in values}.values())
 if len(unique)==1:return unique[0]
 if all(v.get('type')=='object' for v in unique):
  keys=set().union(*(v['properties'] for v in unique));return {'type':'object','properties':{k:merge([v['properties'][k] for v in unique if k in v['properties']]) for k in sorted(keys)}}
 return {'anyOf':unique} if unique else {}
def template(s):
 if s.get('type')=='object':return {k:template(v) for k,v in s['properties'].items()}
 if s.get('type')=='array':return []
 if 'anyOf' in s:return template(next((v for v in s['anyOf'] if not v.get('nullable')),s['anyOf'][0]))
 if s.get('nullable'):return None
 return '{{value}}' if s.get('type')=='string' else False if s.get('type')=='boolean' else 0
groups=collections.defaultdict(list);hosts=collections.Counter();preflight=0
for e in har['log']['entries']:
 r=e['request'];u=urllib.parse.urlsplit(r['url']);hosts[u.hostname]+=1
 if u.hostname!='nextapi.iparsian724.ir' or not u.path.startswith('/api/'):continue
 if r['method']=='OPTIONS':preflight+=1;continue
 p=re.sub(r'(/GetNextBankReceiptByStatement)/[^/]+',r'\1/{statementId}',u.path)
 groups[(r['method'],p)].append(e)
catalog=[];paths={};items=[]
for (method,p),es in groups.items():
 bodies=[];responses=collections.defaultdict(list);query=set();auth=False
 for e in es:
  r=e['request'];auth |= any(h['name'].lower()=='sessionid' for h in r['headers']);query.update(urllib.parse.parse_qs(urllib.parse.urlsplit(r['url']).query));query.update(q['name'] for q in r.get('queryString',[]))
  raw=r.get('postData',{}).get('text','')
  if raw:
   try:bodies.append(schema(json.loads(raw)))
   except ValueError:bodies.append({'type':'string'})
  content=e['response'].get('content',{});text=content.get('text','')
  if content.get('encoding')=='base64':
   import base64
   text=base64.b64decode(text).decode('utf8',errors='replace')
  try:responses[str(e['response']['status'])].append(schema(json.loads(text)))
  except ValueError:responses[str(e['response']['status'])].append({'type':'string'})
 x={'id':p[5:].replace('/','_').replace('{statementId}','by_id').rstrip('_'),'method':method,'path':p,'auth':auth,'bodySchema':merge(bodies),'hasBody':bool(bodies),'queryKeys':sorted(query),'observations':len(es),'responseSchemas':{k:merge(v) for k,v in responses.items()}}
 if bodies and all(b==bodies[0] for b in bodies) and bodies[0] in ({'type':'object','properties':{}},{'nullable':True}):x['defaultBody']={} if bodies[0].get('type')=='object' else None
 catalog.append(x)
 parameters=[{'name':k,'in':'query','schema':{'type':'string'}} for k in sorted(query)]
 if '{statementId}' in p:parameters.append({'name':'statementId','in':'path','required':True,'schema':{'type':'string'}})
 op={'operationId':x['id'],'parameters':parameters,'responses':{k:{'description':'Observed upstream HTTP '+k,'content':{'application/json':{'schema':v}}} for k,v in x['responseSchemas'].items()},'security':[{'sessionId':[]}] if auth else []}
 if bodies:op['requestBody']={'content':{'application/json':{'schema':x['bodySchema']}}}
 paths.setdefault(p,{})[method.lower()]=op
 headers=[{'key':'sessionId','value':'{{sessionId}}'}] if auth else []
 request={'method':method,'header':headers,'url':'{{baseUrl}}'+p.replace('{statementId}','{{statementId}}')+('?'+'&'.join(k+'={{'+k+'}}' for k in sorted(query)) if query else '')}
 if bodies:request['header'].append({'key':'Content-Type','value':'application/json'});request['body']={'mode':'raw','raw':json.dumps(template(x['bodySchema']),indent=2),'options':{'raw':{'language':'json'}}}
 items.append({'name':x['id'],'request':request})
def write(name,obj):(root/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
write('data/endpoints.json',catalog)
write('openapi.json',{'openapi':'3.0.3','info':{'title':'Parsian API','version':'0.2.0'},'servers':[{'url':'https://nextapi.iparsian724.ir'}],'components':{'securitySchemes':{'sessionId':{'type':'apiKey','in':'header','name':'sessionId'}}},'paths':paths})
write('parsian-api.postman_collection.json',{'info':{'name':'Parsian API','schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'},'variable':[{'key':'baseUrl','value':'https://nextapi.iparsian724.ir'},{'key':'sessionId','value':''},{'key':'statementId','value':''}],'item':items})
write('data/har-audit.json',{'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sources':[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'totalEntries':len(har['log']['entries']),'hosts':dict(hosts),'preflightRequests':preflight,'operationalRequests':sum(len(es) for es in groups.values()),'endpoints':len(catalog),'note':'Static assets and frontend navigation are inventoried by host; only captured API operations are callable. Schemas describe observations, not guaranteed bank requirements.'})
print(json.dumps({'endpoints':len(catalog),'requests':sum(len(es) for es in groups.values())}))
