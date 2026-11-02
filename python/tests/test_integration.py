import json
import shutil
import subprocess
from pathlib import Path
import pytest
from parsianapi import Client

@pytest.fixture(scope='module')
def service():
    node=shutil.which('node')
    fixture=Path(__file__).with_name('service-fixture.cjs')
    if not node or not (fixture.parents[2]/'server.js').exists():
        pytest.skip('Node integration requires the complete GitHub source tree')
    process=subprocess.Popen([node,str(fixture)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        line=process.stdout.readline()
        if not line:pytest.fail('Mock service did not start')
        port=json.loads(line)['port']
        yield f'http://127.0.0.1:{port}/v1'
    finally:
        process.terminate()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)

def test_actual_node_service_form_roundtrip(service):
    with Client(service,api_key='fixture-service-key',env_file=False) as client:
        assert client.accounts()['deposits']==[]
        assert client.login('fixture-user','fixture-pass','09120000000')['loggedIn'] is True
        data=client.pol('00123456','IR000000000000000000000000',10000,'00123',reason='LMAP',branch_code='0000')['data']
        assert data['path']=='/api/Transfer/PostPaymentOrder'
        assert data['received']['chSecondPasswordType']=='TRANSFER_SECOND_PASS'
        assert data['received']['secondPassword']=='00123'
        assert data['received']['chPaymentOrderRqBean']['amount']==10000
        otp=client.sheba_code('00123456','IR000000000000000000000000',10000)['data']
        assert otp['path']=='/api/Otp/OtpGenerateForAccountTransfer'
        assert otp['received']['customerNumber']=='synthetic-customer'
        assert 'secondPassword' not in otp['received']
