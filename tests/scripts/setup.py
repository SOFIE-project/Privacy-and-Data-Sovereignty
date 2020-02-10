from indy import anoncreds, crypto, did, ledger, pool, wallet
from indy.error import ErrorCode, IndyError
import json
import sys
import asyncio
import os 

pool_name             = 'Test_pool'
pool_genesis_txn_path = os.getcwd()+'/indy_sample_genesis_txn'
'''
This Steward is part of the indy-sdk testing network
'''
steward = {
    'name': "Steward",
    'wallet_config': json.dumps({'id': 'steward_wallet', "storage_config":{"path":"indy_wallets"}}),
    'wallet_credentials': json.dumps({'key': 'steward_wallet_key'}),
    'seed': '000000000000000000000000Steward1'
}

endorser = {
    'name': "Endorser",
    'wallet_config': json.dumps({'id': 'endorser_wallet', "storage_config":{"path":"indy_wallets"}}),
    'wallet_credentials': json.dumps({'key': 'endorser_wallet_key'}),
    'seed': '00000000000000000000000Endorser1' #used only for testing
}

user = {
    'wallet_config': json.dumps({'id': 'user_wallet', "storage_config":{"path":"indy_wallets"}}),
    'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
    'seed': '000000000000000000000000000User1', #used only for testing
    'msk' : 'msk_key'
}

server = {
    'wallet_config': json.dumps({'id': 'as_wallet',"storage_config":{"path":"indy_wallets"}}),
    'wallet_credentials': json.dumps({'key': 'server_wallet_key'}),
    'seed': '0000000000000000000000000Server1', #used only for testing
    'msk' : 'msk_key'
}

credential = {
    'name': 'Grant',
    'version': '1.0',
    'attributes': ['resources', 'operations']
}

cred_values = json.dumps({
    "resources": {"raw": "sofe-iot.eu", "encoded": "5"}, 
    "operations": {"raw": "get", "encoded": "2"}
})

async def setup():
    print("1. Creating pool")
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
    await pool.set_protocol_version(2)
    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass

    print("2. Opening pool")
    pool_handle = await pool.open_pool_ledger(pool_name, pool_config)
    #################################################
    print("3. Creating Steward wallet and DID")
    try:
        await wallet.create_wallet(steward['wallet_config'], steward['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    steward['wallet']               = await wallet.open_wallet(steward['wallet_config'], steward['wallet_credentials'])        
    steward['did_info']             = json.dumps({'seed': steward['seed']})
    steward['did'], steward['key']  = await did.create_and_store_my_did(steward['wallet'], steward['did_info'])
    #################################################
    print("4. Creating Endorser wallet, DID, and storing it in the ledger")
    try:
        await wallet.create_wallet(endorser['wallet_config'], endorser['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    endorser['wallet']               = await wallet.open_wallet(endorser['wallet_config'], endorser['wallet_credentials'])
    endorser['did_info']             = json.dumps({'seed': endorser['seed']})       
    endorser['did'], endorser['key'] = await did.create_and_store_my_did(endorser['wallet'], endorser['did_info'])
    nym_request                      = await ledger.build_nym_request(steward['did'], endorser['did'], endorser['key'], None, 'TRUST_ANCHOR')
    await ledger.sign_and_submit_request(pool_handle, steward['wallet'], steward['did'], nym_request)
    print("...Endorser DID: " + endorser['did'])
    #################################################
    print("5. Creating user wallet, DID, storing it in the ledger, and creating master secret key")
    try:
        await wallet.create_wallet(user['wallet_config'], user['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    user['wallet']           = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials']) 
    user['did_info']         = json.dumps({'seed': user['seed']})       
    user['did'], user['key'] = await did.create_and_store_my_did(user['wallet'], user['did_info'])
    nym_request              = await ledger.build_nym_request(endorser['did'], user['did'], user['key'], None, None)
    await ledger.sign_and_submit_request(pool_handle, endorser['wallet'], endorser['did'], nym_request)
    try:
        await anoncreds.prover_create_master_secret(user['wallet'], user['msk'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.AnoncredsMasterSecretDuplicateNameError:
            pass 
    #################################################
    print("6. Creating credential schema and storing it the ledger")
    cred_schema_id, cred_schema = await anoncreds.issuer_create_schema(endorser['did'], credential['name'], credential['version'], json.dumps(credential['attributes']))
    print("...cred_schema_id = " + cred_schema_id)
    print("...cred_schema = " + cred_schema)
    schema_request = await ledger.build_schema_request(endorser['did'], cred_schema)
    await ledger.sign_and_submit_request(pool_handle, endorser['wallet'], endorser['did'], schema_request)
    #################################################
    print("7. Creating credential")
    cred_def_id, cred_def = await anoncreds.issuer_create_and_store_credential_def(endorser['wallet'], endorser['did'], cred_schema, 'TAG1', 'CL', json.dumps({"support_revocation": False}))
    print("...cred_def_id = " + cred_def_id)
    print("...cred_def = " + cred_def)
    #################################################
    print("8. Creating credential offer")
    cred_offer = await anoncreds.issuer_create_credential_offer(endorser['wallet'], cred_def_id)
    print("...cred_offer = " + cred_offer)
    #################################################
    print("9. Creating credential request")
    cred_req, cred_req_metadata = await anoncreds.prover_create_credential_req(user['wallet'], user['did'], cred_offer, cred_def, "msk_key")
    #################################################
    print("10.Issuing credential and storing them in user wallet")
    cred, _, _ = await anoncreds.issuer_create_credential(endorser['wallet'], cred_offer, cred_req, cred_values, None, None)
    await anoncreds.prover_store_credential(user['wallet'], None, cred_req_metadata, cred, cred_def, None)
    #################################################
    '''
    The following is used for verifying DIDs without the pool
    '''
    print("11. Creating server wallet")
    try:
        await wallet.create_wallet(server['wallet_config'], server['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    #################################################
    '''
    The following is used for verifying DIDs without the pool
    '''
    print("12. Storing user verkey in server's wallet")
    server['wallet'] = await wallet.open_wallet(server['wallet_config'], server['wallet_credentials'])
    await did.store_their_did(server['wallet'],json.dumps({"did": user['did'], "verkey": user['key']})) 
    #################################################
    print("Cleaning up")
    await wallet.close_wallet(steward['wallet'])
    await wallet.close_wallet(endorser['wallet'])
    await wallet.close_wallet(user['wallet'])
    await wallet.close_wallet(server['wallet'])
    await pool.close_pool_ledger(pool_handle)
    
    print("Creating client configuration file")
    conf = {}
    conf['cred_def_id']    = cred_def_id
    conf['cred_def']       = cred_def
    conf['cred_schema_id'] = cred_schema_id
    conf['cred_schema']    = cred_schema
    with open('conf/agent.conf', 'w') as f:
        json.dump(conf,f)
    conf['pool_name']      = pool_name
    conf['pool_genesis_txn_path'] = '/indy_sample_genesis_txn'
    conf['user']          = user
    with open('conf/client.conf', 'w') as f:
        json.dump(conf,f)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    loop.close()

if __name__ == '__main__':
    main()