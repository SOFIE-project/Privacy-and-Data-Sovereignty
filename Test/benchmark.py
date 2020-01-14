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
import time

pool_name             = 'Test_pool'
pool_genesis_txn_path = 'indy_sample_genesis_txn'
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
    'wallet_credentials': json.dumps({'key': 'endorser_wallet_key'})
}

async def run():
    print("Creating configuration file")
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
    await pool.set_protocol_version(2)
    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            print("...Configuration file already exists. Skipping.")
            pass
    pool_handle = await pool.open_pool_ledger(pool_name, pool_config)

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
            print( await did.list_my_dids_with_meta(steward['wallet']) ) 
            pass

    print("Creating Endorser wallet and DID")
    try:
        await wallet.create_wallet(endorser['wallet_config'], endorser['wallet_credentials'])
        endorser['wallet'] = await wallet.open_wallet(endorser['wallet_config'], endorser['wallet_credentials'])        
        endorser['did'], endorser['key'] = await did.create_and_store_my_did(endorser['wallet'], {})
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            print("...Wallet already exists. Dumping contents.")
            endorser['wallet'] = await wallet.open_wallet(endorser['wallet_config'], endorser['wallet_credentials'])
            print( await did.list_my_dids_with_meta(endorser['wallet']) ) 
            pass
    print("\nCreating professor wallet, DID, and master secret key")
    professor_wallet_config = json.dumps({"id": "professor"})
    professor_wallet_credentials = json.dumps({"key": "password"})
    try:
        await wallet.create_wallet(professor_wallet_config, professor_wallet_credentials)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    professor_wallet = await wallet.open_wallet(professor_wallet_config, professor_wallet_credentials)
    professor_did, professor_verkey = await did.create_and_store_my_did(professor_wallet, "{}")
    start_time = time.time()
    master_secret_id = await anoncreds.prover_create_master_secret(professor_wallet, "master_secret")
    print("--- %s to create a master secret key ---" % (time.time() - start_time))

    print("Closing wallets")
    await wallet.close_wallet(steward['wallet'])
def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()


if __name__ == '__main__':
    main()