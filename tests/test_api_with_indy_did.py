from indy import did,wallet,crypto
from nacl.public import SealedBox
import nacl.encoding
import pytest
import requests
import json
import asyncio
import base64
import datetime
import time

@pytest.fixture(autouse=True, scope="module")
def server():
    import subprocess
    import time
    p1 = subprocess.Popen(['python3', 'PDS/pds.py'])
    #p2 = subprocess.Popen(['python3', 'PDS/pds_admin.py'])
    time.sleep(5) #Otherwise the server is not ready when tests start
    yield
    p1.kill()
    #p2.kill()



@pytest.mark.asyncio
async def test_valid_did():
    user = {
        'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"tests/indy_wallets"}}),
        'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
        'did' : '4qk3Ab43ufPQVif4GAzLUW'
    }
    payload = {'grant-type':'DID', 'grant':user['did'], 'target':'smartlocker1'}
    response  = requests.post("http://localhost:9001/gettoken", data = payload)
    assert(response.status_code == 401)
    challenge = response.text
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    signature = await crypto.crypto_sign(wallet_handle, verkey, challenge.encode())
    signature64 = base64.b64encode(signature)
    exp = time.mktime(datetime.datetime(2020, 4, 1, 23, 59).timetuple())
    payload = {'grant-type':'DID', 'grant':user['did'], 'challenge': challenge, 'proof':signature64}
    response  = requests.post("http://localhost:9001/gettoken", data = payload)
    token = response.text
    assert(response.status_code == 200)
    await wallet.close_wallet(wallet_handle)
'''
@pytest.mark.asyncio
async def test_add_did():
    user = {
        'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"tests/indy_wallets"}}),
        'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
        'did' : '4qk3Ab43ufPQVif4GAzLUW'
    }
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    nbf = time.mktime(datetime.datetime(2020, 4, 1, 00, 00).timetuple())
    exp = time.mktime(datetime.datetime(2020, 4, 1, 23, 59).timetuple()) 
    payload = {'action':'add','did':user['did'], 'verkey': verkey, 'metadata':json.dumps({'aud': 'sofie-iot.eu','nbf':nbf, 'exp': exp})}
    response  = requests.post("http://localhost:9002/", data = payload).text
    response =json.loads(response)
    assert(response['code'] == 200)
    payload = {'action':'get', 'did':user['did']}
    response  = requests.post("http://localhost:9002/", data = payload).text
    response =json.loads(response)
    assert(response['code'] == 200)
    await wallet.close_wallet(wallet_handle)
    '''