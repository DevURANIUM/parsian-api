import asyncio
import json
import os
from urllib.parse import parse_qs
import httpx
import pytest
from parsianapi import Client, AsyncClient, ApiError, TransportError, ProtocolError
from parsianapi._core import OPERATIONS

@pytest.fixture
def requests():
    return []

@pytest.fixture
def client(requests):
    def handle(request):
        requests.append(request)
        return httpx.Response(200,json={'status':0,'data':{'nested':[0,False,None]}})
    with Client(api_key='service-secret',env_file=False,transport=httpx.MockTransport(handle)) as c:
        yield c

def fields(request):
    return parse_qs(request.content.decode(),keep_blank_values=True)

def sample(schema):
    if 'example' in schema:return dict(schema['example'])
    if schema.get('type')=='object':return {k:sample(v) for k,v in schema.get('properties',{}).items()}
    if schema.get('type')=='array':return []
    if 'anyOf' in schema:return sample(schema['anyOf'][0])
    if schema.get('type')=='boolean':return False
    if schema.get('type') in ('integer','number'):return 1
    if schema.get('nullable'):return None
    return 'fixture'

@pytest.mark.parametrize('op',OPERATIONS,ids=lambda op:op['command'])
def test_all_sync_operation_routes(op,client,requests):
    kwargs={}
    if op['bodySchema'].get('type')=='array':kwargs['items']=[]
    else:kwargs.update(sample(op['bodySchema']) if op['bodySchema'].get('type')=='object' else {})
    for p in op['parameters']:
        if p['in']=='path':kwargs[p['name']]='fixture/id'
    data=client.operation(op['command'],**kwargs)
    assert data['data']['nested']==[0,False,None]
    request=requests[-1]
    assert request.method==op['method']
    assert request.headers['x-api-key']=='service-secret'
    assert request.url.host=='127.0.0.1'
    if op['method']=='POST':assert request.headers['content-type'].startswith('application/x-www-form-urlencoded')

@pytest.mark.parametrize('op',OPERATIONS,ids=lambda op:op['command'])
def test_all_async_operation_routes(op):
    async def check():
        seen=[]
        def handle(request):seen.append(request);return httpx.Response(200,json={'ok':True})
        async with AsyncClient(api_key='key',env_file=False,transport=httpx.MockTransport(handle)) as c:
            kwargs={}
            if op['bodySchema'].get('type')=='array':kwargs['items']=[]
            elif op['bodySchema'].get('type')=='object':kwargs.update(sample(op['bodySchema']))
            for p in op['parameters']:
                if p['in']=='path':kwargs[p['name']]='fixture'
            assert await c.operation(op['command'],**kwargs)=={'ok':True}
            assert seen[0].method==op['method']
    asyncio.run(check())

def test_read_helpers_and_query_encoding(client,requests):
    client.transactions('00123456',page=2,size=10,from_date='2026-10-01T00:01:00.000Z')
    assert requests[-1].url.params['account']=='00123456'
    assert requests[-1].url.params['fromDate']=='2026-10-01T00:01:00.000Z'
    assert 'page=2' in str(requests[-1].url)
    with pytest.raises(ValueError):client.transactions('00123456',page=-1)
    client.transaction('id/with/slash')
    assert b'id%2Fwith%2Fslash' in requests[-1].url.raw_path

@pytest.mark.parametrize('method,kind,mode',[('pol','pol','fixed'),('sheba','sheba','fixed'),('pol_sms','pol/sms','sms'),('sheba_sms','sheba/sms','sms')])
def test_transfer_helpers_are_form_encoded(method,kind,mode,client,requests):
    extra={'branch_code':'0000'} if method.startswith('pol') else {}
    getattr(client,method)('00123456','IR000000000000000000000000',10000,'00123',reason='LMAP',**extra)
    r=requests[-1]
    assert r.url.path.endswith('/'+kind)
    assert fields(r)['from']==['00123456']
    assert fields(r)['pass']==['00123']
    assert fields(r)['amount']==['10000']
    with pytest.raises(ValueError):getattr(client,method)('00123456','IR000000000000000000000000',True,'00123',reason='LMAP',**extra)

def test_sms_helpers_do_not_submit_money(client,requests):
    client.pol_code('00123456','IR000000000000000000000000',10000)
    assert requests[-1].url.path.endswith('/pol/code')
    assert 'pass' not in fields(requests[-1])

def test_nested_fields_and_arrays(client,requests):
    client.operation('workflow-event',workflow_instance_id='id',event_name='TransferSubmission',event_data={'card_transfer_data':{'amount':'10000'}})
    assert fields(requests[-1])['EventData.cardTransferData.amount']==['10000']
    client.operation('config-save',items=[{'key':'demo','value':'false','type':'boolean'}])
    assert fields(requests[-1])['0.value']==['false']

def test_dotenv_and_explicit_priority(tmp_path,monkeypatch,requests):
    for key in ['PARSIAN_USER','PARSIAN_PASS','PARSIAN_MOBILE','PARSIAN_API_KEY','PARSIAN_API_URL']:monkeypatch.delenv(key,raising=False)
    env=tmp_path/'.env';env.write_text('PARSIAN_USER=file-user\nPARSIAN_PASS="file # secret"\nPARSIAN_MOBILE=09120000000\nPARSIAN_API_KEY=file-key\n')
    monkeypatch.setenv('PARSIAN_USER','shell-user')
    def handle(r):requests.append(r);return httpx.Response(200,json={'loggedIn':True})
    with Client(api_key='explicit-key',env_file=env,transport=httpx.MockTransport(handle)) as c:
        c.login()
        assert 'file # secret' not in repr(c)
    assert fields(requests[-1])['username']==['shell-user']
    assert fields(requests[-1])['password']==['file # secret']
    assert requests[-1].headers['x-api-key']=='explicit-key'

def test_errors_keep_payload_without_printing_secrets():
    payload={'error':'private-secret','code':'SESSION_EXPIRED','nextAction':'login','bankStatus':1}
    with Client(env_file=False,transport=httpx.MockTransport(lambda r:httpx.Response(401,json=payload))) as c:
        with pytest.raises(ApiError) as caught:c.balance()
        assert caught.value.payload==payload
        assert caught.value.next_action=='login'
        assert 'private-secret' not in str(caught.value)

def test_transport_error_is_uncertain_for_post_and_not_retried():
    calls=[]
    def handle(r):calls.append(r);raise httpx.ReadTimeout('timeout',request=r)
    with Client(env_file=False,transport=httpx.MockTransport(handle)) as c:
        with pytest.raises(TransportError) as caught:c.pol('001234','IR000000000000000000000000',10000,'secret',reason='LMAP',branch_code='0000')
        assert caught.value.request_may_have_succeeded
        assert len(calls)==1

def test_redirects_malformed_json_and_external_paths_are_rejected():
    seen=[]
    def redirect(r):seen.append(r);return httpx.Response(302,headers={'Location':'https://untrusted.invalid/'})
    with Client(env_file=False,transport=httpx.MockTransport(redirect)) as c:
        with pytest.raises(ApiError):c.accounts()
        assert len(seen)==1
        with pytest.raises(ValueError):c.request('GET','https://untrusted.invalid/')
        assert len(seen)==1
    with Client(env_file=False,transport=httpx.MockTransport(lambda r:httpx.Response(200,text='<html>broken</html>'))) as c:
        with pytest.raises(ProtocolError):c.accounts()

@pytest.mark.parametrize('url',['https://user:secret@example.com','https://example.com?key=value','not-a-url'])
def test_invalid_service_urls(url):
    with pytest.raises(ValueError):Client(base_url=url,env_file=False)
def test_login_can_delegate_credentials_to_the_server(client,requests,monkeypatch):
    client._settings={}
    client.login()
    assert fields(requests[-1])=={}
    with pytest.raises(ValueError):client.login(username='')

def test_cli_nested_array_fields(monkeypatch,capsys):
    from parsianapi import cli
    seen=[]
    real=Client
    monkeypatch.setattr(cli,'Client',lambda *a,**kw:real(env_file=False,transport=httpx.MockTransport(lambda r:(seen.append(r) or httpx.Response(200,json={'ok':True})))))
    assert cli.main(['config-save','--field','items.0.key=demo','--field','items.0.value=false','--field','items.0.type=boolean'])==0
    assert fields(seen[0])['0.key']==['demo']
