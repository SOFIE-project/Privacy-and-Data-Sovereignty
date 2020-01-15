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

# Begin configurarion
pool_name             = 'Test_pool'
pool_genesis_txn_path = os.getcwd()+'/indy_sample_genesis_txn'

endorser = {
    'did': "W6xGRF1zBKGMKYp2cNKasC",
}

user_wallet = {
    'wallet_config': json.dumps({'id': 'client_wallet'}),
    'wallet_credentials': json.dumps({'key': 'client_wallet_key'}),
    'seed': '000000000000000000000000000user1' #used only for CI/CD pursposed
}

#End configuration

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

async def create_wallet(wallet_config, wallet_credentials):
    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    #Creating master secre key
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
    await anoncreds.prover_create_master_secret(wallet_handle, "msk_key")
    await wallet.close_wallet(wallet_handle)


async def get_ver_key(pool_handle, wallet_handle, target_did):
    ver_key = await did.key_for_did(pool_handle, wallet_handle, target_did)
    return ver_key
    
'''
async def():
    pool_handle   = await open_pool()
    wallet_handle = await create_and_open_wallet(client['wallet_config'], client['wallet_credentials'])
    endorser_key  = await get_ver_key( pool_handle, wallet_handle, endorser['did'])
    print (endorser_key)
    await wallet.close_wallet(wallet_handle)
'''

async def generate(wallet_config, wallet_credentials):
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
    id, verkey    = await did.create_and_store_my_did(wallet_handle, json.dumps({'seed': user_wallet['seed']}))
    nym_request   = await ledger.build_nym_request(endorser['did'], id, verkey, None, None)
    print(nym_request)
    await wallet.close_wallet(wallet_handle)

async def create_credential_request(wallet_config, wallet_credentials,cred_def, offer):
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
    dids          = json.loads( await did.list_my_dids_with_meta(wallet_handle) )
    user_did      = dids[1]['did']
    cred_request, cred_request_metadata =  await anoncreds.prover_create_credential_req(wallet_handle, user_did, offer, cred_def, "msk_key")
    print("Credential request : ", cred_request)
    print("Credential request metadata: ", cred_request_metadata)
    await wallet.close_wallet(wallet_handle)

async def get_credential_definition(wallet_config, wallet_credentials,cred_def_id):
    pool_handle   = await open_pool()
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
    dids          = json.loads( await did.list_my_dids_with_meta(wallet_handle) )
    user_did      = dids[0]['did']
    get_cred_def_request = await ledger.build_get_cred_def_request(user_did,cred_def_id)
    get_cred_def_response = await ledger.submit_request(pool_handle, get_cred_def_request)
    transcript_cred_def   = await ledger.parse_get_cred_def_response(get_cred_def_response)
    print(transcript_cred_def)
    await wallet.close_wallet(wallet_handle)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--setup', help="Creates wallet", action='store_true')
    parser.add_argument('-g', '--generate', help="Generate a DID, stores it in the wallet, and outputs the nym request", action='store_true')
    parser.add_argument('-c', '--credential', dest='credef', type=str, help="Creates and outputs a credential request for the provided credef. Use with -o")
    parser.add_argument('-o', '--offer', dest='offer', type=str, help="The crendetial offer. Use with -c")
    args = parser.parse_args()
    if(args.setup == True):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(create_wallet(user_wallet['wallet_config'], user_wallet['wallet_credentials']))
        loop.close()
    if(args.generate == True):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(generate(user_wallet['wallet_config'], user_wallet['wallet_credentials']))
        loop.close()
    if(args.credef):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(get_credential_definition(user_wallet['wallet_config'], user_wallet['wallet_credentials'], args.credef)) #, args.offer))
        loop.close()


if __name__ == '__main__':
    main()
