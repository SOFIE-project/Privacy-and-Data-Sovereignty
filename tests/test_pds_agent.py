import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../PDS/')

from indy import did,wallet,crypto
from pds_agent import PDS_agent
import pytest
import requests
import json
import asyncio
import base64
import datetime
import time

@pytest.yield_fixture(scope='module')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="module")
async def server():
    import subprocess
    import time
    p1 = subprocess.Popen(['python3', 'PDS/pds.py'])
    p2 = subprocess.Popen(['python3', 'PDS/pds_admin.py'])
    time.sleep(5) #Otherwise the server is not ready when tests start
    '''
    Add a DID to PDS server wallet
    '''
    user = {
        'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"tests/indy_wallets"}}),
        'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
        'did' : '4qk3Ab43ufPQVif4GAzLUW'
    }
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    nbf = time.mktime(datetime.datetime(2020, 6, 1, 00, 00).timetuple())
    exp = time.mktime(datetime.datetime(2020, 6, 1, 23, 59).timetuple()) 
    payload = {'action':'add','did':user['did'], 'verkey': verkey, 'metadata':json.dumps({'aud': 'locker1.sofie-iot.eu','nbf':nbf, 'exp': exp})}
    response  = requests.post("http://localhost:9002/", data = payload).text
    response =json.loads(response)
    assert(response['code'] == 200)
    await wallet.close_wallet(wallet_handle)
    yield
    p1.kill()
    p2.kill()

@pytest.mark.asyncio
async def test_valid_did():
    user = {
        'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"tests/indy_wallets"}}),
        'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
        'did' : '4qk3Ab43ufPQVif4GAzLUW'
    }
    token = await PDS_agent.get_token_from_did("http://localhost:9001", user['did'], "locker1.sofie-iot.eu", user['wallet_config'], user['wallet_credentials'])
    print(token)
    assert('token' != "")