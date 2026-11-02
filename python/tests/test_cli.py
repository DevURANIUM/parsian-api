import json
from urllib.parse import parse_qs
import httpx
import pytest
from parsianapi import Client
from parsianapi import cli

def fake_client(monkeypatch,handler):
    real=Client
    monkeypatch.setattr(cli,'Client',lambda base_url=None,api_key=None,**kw:real(base_url or 'http://127.0.0.1:3101',api_key or 'test-key',transport=httpx.MockTransport(handler),**kw))

def test_cli_login_reads_env_without_prompt(tmp_path,monkeypatch,capsys):
    env=tmp_path/'.env';env.write_text('PARSIAN_USER=demo\nPARSIAN_PASS="secret # literal"\nPARSIAN_MOBILE=09120000000\n')
    for key in ('PARSIAN_USER','PARSIAN_PASS','PARSIAN_MOBILE'):monkeypatch.delenv(key,raising=False)
    seen=[]
    fake_client(monkeypatch,lambda r:(seen.append(r) or httpx.Response(200,json={'loggedIn':True})))
    monkeypatch.setattr('builtins.input',lambda *args:pytest.fail('unexpected prompt'))
    monkeypatch.setattr(cli.getpass,'getpass',lambda *args:pytest.fail('unexpected secret prompt'))
    assert cli.main(['--env-file',str(env),'login'])==0
    assert parse_qs(seen[0].content.decode())['password']==['secret # literal']
    assert 'secret # literal' not in capsys.readouterr().out

def test_cli_fixed_transfer_and_errors_are_structured(monkeypatch,capsys):
    seen=[]
    fake_client(monkeypatch,lambda r:(seen.append(r) or httpx.Response(200,json={'status':0})))
    assert cli.main(['pol','00123456','IR000000000000000000000000','10000','--password','00123','--reason','LMAP','--branch','0000'])==0
    assert seen[0].url.path=='/v1/pol'
    assert parse_qs(seen[0].content.decode())['pass']==['00123']
    assert cli.main(['--json-errors','transactions','00123456','--page','-1'])==1

def test_cli_code_is_string_and_bank_errors_are_structured(monkeypatch,capsys):
    seen=[]
    fake_client(monkeypatch,lambda r:(seen.append(r) or httpx.Response(401,json={'error':'expired','code':'SESSION_EXPIRED','nextAction':'login'})))
    assert cli.main(['--json-errors','otp','00123','09120000000'])==1
    assert parse_qs(seen[0].content.decode())['code']==['00123']
    assert json.loads(capsys.readouterr().err)['code']=='SESSION_EXPIRED'
