import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../PDS/')

from indy import did,wallet,crypto
from web3 import Web3
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
    global w3, abi, account, address
    p3 = subprocess.Popen(['ganache-cli', '-m', 'myth like bonus scare over problem client lizard pioneer submit female collect']) #use this mnemonic to much the contract address in configuration
    time.sleep(10)
    p1 = subprocess.Popen(['python3', 'PDS/pds.py'])
    p2 = subprocess.Popen(['python3', 'PDS/pds_admin.py'])
    time.sleep(5) #Otherwise the server is not ready when tests start
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
    with open('conf/contract/build/PDS.abi', 'r') as myfile:
        abi = myfile.read()
    with open('conf/contract/build/PDS.bin', 'r') as myfile:
        binfile = myfile.read()
    account = w3.eth.accounts[0]
    PDSContract = w3.eth.contract(abi=abi, bytecode=binfile)
    tx_hash = PDSContract.constructor().transact({'from': account})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    address = tx_receipt.contractAddress
    yield
    p1.kill()
    p2.kill()
    p3.kill()


@pytest.mark.asyncio
async def test_valid_did():
    user = {
        'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"tests/indy_wallets"}}),
        'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
        'did' : '4qk3Ab43ufPQVif4GAzLUW'
    }
    payload = {'grant-type':'DID', 'grant':user['did'], 'target':'smartlocker1'}
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    assert(response['code'] == 401)
    challenge = response['challenge']
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    signature = await crypto.crypto_sign(wallet_handle, verkey, challenge.encode())
    signature64 = base64.b64encode(signature)
    exp = time.mktime(datetime.datetime(2020, 4, 1, 23, 59).timetuple())
    payload = {'grant-type':'DID', 'grant':user['did'], 'challenge': challenge, 'proof':signature64}
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    assert(response['code'] == 200)
    await wallet.close_wallet(wallet_handle)

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
@pytest.mark.asyncio
async def test_valid_did_ecn_token():
    user = {
        'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"tests/indy_wallets"}}),
        'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
        'did' : '4qk3Ab43ufPQVif4GAzLUW'
    }
    privateKeyHex = 'd686cb5b1e7866c657af66b6c365dd8f1523678dbf1a9d0344c5e9c38847c034'
    publicKeyHex =  '34a0d7e2c95b24c9c87e47ce4e528c3814a8516528b4095c84b49908390b7a24'
    payload = {'grant-type':'DID', 'grant':user['did'], 'target':"sofie-iot.eu", 'token-type':'DID-encrypted', 'subject':user['did'] }
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    assert(response['code'] == 401)
    challenge = response['challenge']
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    signature = await crypto.crypto_sign(wallet_handle, verkey, challenge.encode())
    signature64 = base64.b64encode(signature)
    nbf = time.mktime(datetime.datetime(2020, 4, 1, 00, 00).timetuple())
    exp = time.mktime(datetime.datetime(2020, 4, 1, 23, 59).timetuple()) 
    payload = {'grant-type':'auth_code', 'grant':'shared_secret_key', 'metadata':json.dumps({'aud': 'sofie-iot.eu','nbf':nbf, 'exp': exp}), 'enc_key':publicKeyHex}
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    enc64 = response['message']
    enc   = base64.urlsafe_b64decode(enc64)
    private_key = nacl.public.PrivateKey(privateKeyHex,nacl.encoding.HexEncoder)
    sealed_box = SealedBox(private_key)
    msg = sealed_box.decrypt(enc)

    assert(response['code'] == 200)
    await wallet.close_wallet(wallet_handle)

@pytest.mark.asyncio
async def test_valid_did_ecn_token_with_logging():
    global w3, abi, account, address
    user = {
        'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"tests/indy_wallets"}}),
        'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
        'did' : '4qk3Ab43ufPQVif4GAzLUW'
    }
    payload = {'grant-type':'DID', 'grant':user['did'], 'target':"sofie-iot.eu", 'token-type':'DID-encrypted', 'subject':user['did'] }
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    assert(response['code'] == 401)
    challenge = response['challenge']
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    signature = await crypto.crypto_sign(wallet_handle, verkey, challenge.encode())
    signature64 = base64.b64encode(signature)
    payload = {'grant-type':'DID', 'grant':user['did'], 'challenge': challenge, 'proof':signature64, 'target':'sofie-iot.eu', 'token-type':'DID-encrypted', 'subject':user['did'], 'log-token':'True'}
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    enc64 = response['message']
    print(enc64)
    PDSContract_instance = w3.eth.contract(abi=abi, address=address)
    logged_did, logged_token = PDSContract_instance.functions.get_token(0).call()
    print(logged_token)
    enc   = base64.urlsafe_b64decode(enc64)
    msg   = await crypto.anon_decrypt (wallet_handle, verkey, enc)
    assert(response['code'] == 200)
    assert(enc64 == logged_token.decode('utf-8'))
    await wallet.close_wallet(wallet_handle)
'''

@pytest.mark.asyncio
async def test_valid_auth_code_ecn_token():
    privateKeyHex = 'd686cb5b1e7866c657af66b6c365dd8f1523678dbf1a9d0344c5e9c38847c034'
    publicKeyHex =  '34a0d7e2c95b24c9c87e47ce4e528c3814a8516528b4095c84b49908390b7a24'
    nbf = time.mktime(datetime.datetime(2020, 4, 1, 00, 00).timetuple())
    exp = time.mktime(datetime.datetime(2020, 4, 1, 23, 59).timetuple()) 
    payload = {'grant-type':'auth_code', 'grant':'shared_secret_key', 'metadata':json.dumps({'aud': 'sofie-iot.eu','nbf':nbf, 'exp': exp}), 'enc-key':publicKeyHex}
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    enc64 = response['message']
    enc   = base64.urlsafe_b64decode(enc64)
    private_key = nacl.public.PrivateKey(privateKeyHex,nacl.encoding.HexEncoder)
    sealed_box = SealedBox(private_key)
    msg = sealed_box.decrypt(enc)
    assert(response['code'] == 200)

@pytest.mark.asyncio
async def test_valid_auth_code_ecn_token_with_logging():
    global w3, abi, account, address
    privateKeyHex = 'd686cb5b1e7866c657af66b6c365dd8f1523678dbf1a9d0344c5e9c38847c034'
    publicKeyHex =  '34a0d7e2c95b24c9c87e47ce4e528c3814a8516528b4095c84b49908390b7a24'
    nbf = time.mktime(datetime.datetime(2020, 4, 1, 00, 00).timetuple())
    exp = time.mktime(datetime.datetime(2020, 4, 1, 23, 59).timetuple()) 
    payload = {'grant-type':'auth_code', 'grant':'shared_secret_key', 'metadata':json.dumps({'aud': 'sofie-iot.eu','nbf':nbf, 'exp': exp}), 'enc-key':publicKeyHex, 'log-token': '0x68656c6c6f20776f726c64'}
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    enc64 = response['message']
    PDSContract_instance = w3.eth.contract(abi=abi, address=address)
    logged_metadata, logged_enc_token = PDSContract_instance.functions.get_token(0).call()
    assert(response['code'] == 200)
    assert(enc64 == logged_enc_token.decode('utf-8'))