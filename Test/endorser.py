'''
Run indy sdk idny-pool sample docker file
(https://github.com/hyperledger/indy-sdk#how-to-start-local-nodes-pool-with-docker)

docker build -f ci/indy-pool.dockerfile -t indy_pool .
docker run -itd -p 9701-9708:9701-9708 indy_pool
'''
from indy import anoncreds, crypto, did, ledger, pool, wallet
from indy.error import ErrorCode, IndyError
import json
import sys
import asyncio
import os
import argparse  

pool_name             = 'Test_pool'
pool_genesis_txn_path = os.getcwd()+'/indy_sample_genesis_txn'
'''
This Steward is part of the indy-sdk testing network
'''
steward = {
    'name': "Steward",
    'wallet_config': json.dumps({'id': 'steward_wallet'}),
    'wallet_credentials': json.dumps({'key': 'steward_wallet_key'}),
    'seed': '000000000000000000000000Steward1'
}

endorser = {
    'name': "Endorser",
    'wallet_config': json.dumps({'id': 'endorser_wallet'}),
    'wallet_credentials': json.dumps({'key': 'endorser_wallet_key'}),
}

async def open_pool():
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
    '''
    await pool.set_protocol_version(2)
    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            print("...Configuration file already exists. Skipping.")
            pass
    '''
    pool_handle = await pool.open_pool_ledger(pool_name, pool_config)
    return pool_handle

async def setup():
    pool_handle = await open_pool()

    print("Creating Steward wallet")
    try:
        await wallet.create_wallet(steward['wallet_config'], steward['wallet_credentials'])
        steward['wallet'] = await wallet.open_wallet(steward['wallet_config'], steward['wallet_credentials'])        
        steward['did_info'] = json.dumps({'seed': steward['seed']})
        steward['did'], steward['key'] = await did.create_and_store_my_did(steward['wallet'], steward['did_info'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            print("...Wallet already exists. Dumping contents.")
            steward['wallet'] = await wallet.open_wallet(steward['wallet_config'], steward['wallet_credentials'])
            wallet_content  = json.loads( await did.list_my_dids_with_meta(steward['wallet']) )
            steward['did']  = wallet_content[0]['did']
            steward['key']  = wallet_content[0]['verkey']
            print( steward['did'] ) 
            pass

    print("Creating Endorser wallet and DID")
    try:
        await wallet.create_wallet(endorser['wallet_config'], endorser['wallet_credentials'])
        endorser['wallet'] = await wallet.open_wallet(endorser['wallet_config'], endorser['wallet_credentials'])        
        endorser['did'], endorser['key'] = await did.create_and_store_my_did(endorser['wallet'], "{}")
        #write endorser DID in the ledger
        nym_request = await ledger.build_nym_request(steward['did'], endorser['did'], endorser['key'], None, 'TRUST_ANCHOR')
        await ledger.sign_and_submit_request(pool_handle, steward['wallet'], steward['did'], nym_request)
        print ("Endorser DID created and stored in the ledger")
        print (endorser['did'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            print("...Wallet already exists. Dumping contents.")
            endorser['wallet'] = await wallet.open_wallet(endorser['wallet_config'], endorser['wallet_credentials'])
            print( await did.list_my_dids_with_meta(endorser['wallet']) ) 
            pass

    print("Closing wallets")
    await wallet.close_wallet(steward['wallet'])

async def create_credential_definition(schema):
    pool_handle   = await open_pool()
    wallet_handle = await wallet.open_wallet(endorser['wallet_config'], endorser['wallet_credentials'])
    dids          = json.loads( await did.list_my_dids_with_meta(wallet_handle) )
    endorser_did  = dids[0]['did']
    schema_def = json.loads(schema)
    def_id, def_schema = await anoncreds.issuer_create_schema(endorser_did, schema_def['name'], schema_def['version'], json.dumps(schema_def['attributes']))
    schema_request = await ledger.build_schema_request(endorser_did, def_schema)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, endorser_did, schema_request)
    print("Schema id: ", def_id)
    print("Schema: ", def_schema)
    #cred_def = {'tag': 'TAG1', 'type': 'CL', 'config': {"support_revocation": False}}
    cred_id, cred = await anoncreds.issuer_create_and_store_credential_def(wallet_handle, endorser_did, def_schema, 'TAG1', 'CL', json.dumps({"support_revocation": False}))
    print("Credential id: ", cred_id)
    print("Credential: ", cred)
    cred_def_request = await ledger.build_cred_def_request(endorser_did, cred)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, endorser_did, cred_def_request)
    await wallet.close_wallet(wallet_handle)

async def create_credential_offer(cred_id):
    wallet_handle = await wallet.open_wallet(endorser['wallet_config'], endorser['wallet_credentials'])
    cred_offer = await anoncreds.issuer_create_credential_offer(wallet_handle, cred_id)
    print(cred_offer)
    await wallet.close_wallet(wallet_handle)

async def sign_and_submit_nym(nym_request):
    pool_handle   = await open_pool()
    wallet_handle = await wallet.open_wallet(endorser['wallet_config'], endorser['wallet_credentials'])
    dids          = json.loads( await did.list_my_dids_with_meta(wallet_handle) )
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, dids[0]['did'], nym_request)
    await wallet.close_wallet(wallet_handle)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--register', dest='nym', type=str, help="Signs a NYM and submits it to the ledger")
    parser.add_argument('-d', '--definition', dest='schema', type=str, help="Creates credentials definition based on the provided SCHEMA and outputs the definition did")
    parser.add_argument('-o', '--offer', dest='credid', type=str, help="Creates and outputs a credential offer for the provided credid")
    args = parser.parse_args()
    if (args.nym):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sign_and_submit_nym(args.register))
        loop.close()
    if (args.schema):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(create_credential_definition(args.schema))
        loop.close()
    if(args.credid):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(create_credential_offer(args.credid))
        loop.close()

    


if __name__ == '__main__':
    main()