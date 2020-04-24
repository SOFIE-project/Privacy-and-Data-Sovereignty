import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../PDS/')

from indy import anoncreds, crypto, did, ledger, pool, wallet
from indy.error import ErrorCode, IndyError
from indy_agent import Indy
import pytest
import asyncio
import json
import base64
import datetime
import time

user = {
    'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"tests/indy_wallets"}}),
    'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
    'seed': '000000000000000000000000000User1', #used only for testing
    'msk' : 'msk_key',
    'did' : '4qk3Ab43ufPQVif4GAzLUW'
}

server = {
    'wallet_config': json.dumps({'id': 'as_wallet',"storage_config":{"path":"tests/indy_wallets"}}),
    'wallet_credentials': json.dumps({'key': 'server_wallet_key'}),
    'seed': '0000000000000000000000000Server1', #used only for testing
    'msk' : 'msk_key'
}

cred_schema_id = 'NKGKtcNwssToP5f7uhsEs4:2:gra:1.0'
cred_def_id    = "NKGKtcNwssToP5f7uhsEs4:3:CL:13:tag_2"

                  

@pytest.yield_fixture(scope='module')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="module")
async def server():
    global pool_handle
    pool_name             = 'Test_pool'
    pool_genesis_txn_path = '/../conf/indy/indy_sample_genesis_txn'
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
    await pool.set_protocol_version(2)
    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    pool_handle = await pool.open_pool_ledger(pool_name, pool_config)
    yield
    await pool.close_pool_ledger(pool_handle)

#python3 -m pytest tests/test_indy_agent.py -s --tb=short -k test_valid_vc
@pytest.mark.asyncio
async def test_valid_vc():
    global pool_handle, cred_def_id
    code, response = await Indy.verify_vc()
    assert (code == 401)
    challenge           = base64.b64decode(response['challenge']).decode()
    wallet_handle       = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    cred_schema_request = await ledger.build_get_schema_request(user['did'], cred_schema_id)
    pool_response       = await ledger.sign_and_submit_request(pool_handle, wallet_handle, user['did'], cred_schema_request)
    _, cred_schema      = await ledger.parse_get_schema_response(pool_response)
    cred_def_request    = await ledger.build_get_cred_def_request(user['did'], cred_def_id)
    pool_response       = await ledger.sign_and_submit_request(pool_handle, wallet_handle, user['did'], cred_def_request)
    _,cred_def          = await ledger.parse_get_cred_def_response(pool_response)    
    cred_iter           = await anoncreds.prover_search_credentials_for_proof_req(wallet_handle, challenge, None)
    creds               = await anoncreds.prover_fetch_credentials_for_proof_req(cred_iter, 'attr1_referent', 1)
    cred_info           = json.loads(creds)[0]['cred_info']
    schemas             = json.dumps({cred_schema_id: json.loads(cred_schema)})
    cred_defs           = json.dumps({cred_def_id: json.loads(cred_def)})
    creds               = json.dumps({
                           'self_attested_attributes': {},
                           'requested_attributes': {
                               'attr1_referent': {
                                   'cred_id': cred_info['referent'],
                                   'revealed': True
                               }
                           },
                           'requested_predicates': {}
                          })
    proof               = await anoncreds.prover_create_proof(wallet_handle, challenge, creds, user['msk'], schemas, cred_defs, "{}")
    code, response      = await Indy.verify_vc(challenge, proof, schemas, cred_defs)
    assert (code == 200)
    
    await wallet.close_wallet(wallet_handle)
    



@pytest.mark.asyncio
async def test_valid_did():
    code, response = await Indy.verify_did(user['did'])
    assert (code == 401)
    challenge = response['challenge']
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    signature = await crypto.crypto_sign(wallet_handle, verkey, challenge.encode())
    signature64 = base64.b64encode(signature)
    server_wallet_handle = await wallet.open_wallet( server['wallet_config'], server['wallet_credentials'])
    code, response = await Indy.verify_did(user['did'], challenge, signature64,server_wallet_handle,"", True)
    assert (code == 200)
    await wallet.close_wallet(wallet_handle)
    await wallet.close_wallet(server_wallet_handle)

@pytest.mark.asyncio
async def test_add_did():
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    server_wallet_handle = await wallet.open_wallet( server['wallet_config'], server['wallet_credentials'])
    nbf = time.mktime(datetime.datetime(2020, 4, 1, 00, 00).timetuple())
    exp = time.mktime(datetime.datetime(2020, 4, 1, 23, 59).timetuple()) 
    code, response = await Indy.add_did_to_wallet(server_wallet_handle, user['did'], verkey, json.dumps({'aud': 'sofie-iot.eu','nbf':nbf, 'exp': exp}) )
    assert (code == 200)
    code, response = await Indy.get_did_metadata(server_wallet_handle, user['did'])
    assert (code == 200)
    await wallet.close_wallet(wallet_handle)
    await wallet.close_wallet(server_wallet_handle)

@pytest.mark.asyncio
async def test_encrypt():
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    server_wallet_handle = await wallet.open_wallet( server['wallet_config'], server['wallet_credentials'])
    code, response = await Indy.encrypt_for_did(user['did'], "Hello World",server_wallet_handle,"", True)
    assert (code == 200)
    enc64 = response['message']
    enc   = base64.urlsafe_b64decode(enc64)
    msg   = await crypto.anon_decrypt (wallet_handle, verkey, enc)
    assert (msg.decode() == "Hello World")
    await wallet.close_wallet(wallet_handle)
    await wallet.close_wallet(server_wallet_handle)
