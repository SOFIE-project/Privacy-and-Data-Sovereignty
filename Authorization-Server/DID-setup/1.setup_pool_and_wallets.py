from indy import anoncreds, crypto, did, ledger, pool, wallet
from indy.error import ErrorCode, IndyError
import json
import sys
import asyncio

pool_name             = 'SOFIE'
pool_genesis_txn_path = "INSERT PATH"
steward_id            = "aueb_steward"
steward_seed          = "INSERT SEED"
steward_conf_did      = "INSERT DID"
steward_wallet_pass   = ""
aueb_trustee_id       = "aueb_trustee"
aueb_wallet_pass      = ""
professor_id          = "professor"
professor_wallet_pass = ""
professor_master_secr = "master_secret"
as_id                 = "auth-server"
as_wallet_pass        = ""


async def run():
    print("\nStarting")
    pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
    await pool.set_protocol_version(2)
    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    pool_handle = await pool.open_pool_ledger(pool_name, pool_config)

    print("\nCreating Steward wallet and DID")
    steward_wallet_config = json.dumps({"id": steward_id})
    steward_wallet_credentials = json.dumps({"key": steward_wallet_pass })
    try:
        await wallet.create_wallet(steward_wallet_config, steward_wallet_credentials)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    steward_wallet = await wallet.open_wallet(steward_wallet_config, steward_wallet_credentials)
    steward_did_info = {'did':steward_conf_did,'seed': steward_seed }
    (steward_did, steward_key) = await did.create_and_store_my_did(steward_wallet, json.dumps(steward_did_info))

    print("\nCreating AUEB trustee wallet and DID")
    aueb_wallet_config = json.dumps({"id": aueb_trustee_id})
    aueb_wallet_credentials = json.dumps({"key": aueb_wallet_pass})
    try:
        await wallet.create_wallet(aueb_wallet_config, aueb_wallet_credentials)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    aueb_wallet = await wallet.open_wallet(aueb_wallet_config, aueb_wallet_credentials)
    aueb_did, aueb_verkey = await did.create_and_store_my_did(aueb_wallet, "{}")

    print('\nBuilding NYM request to add Trust Anchor to the ledger')
    nym_transaction_request = await ledger.build_nym_request(submitter_did=steward_did,
                                                            target_did=aueb_did,
                                                            ver_key=aueb_verkey,
                                                            alias=None,
                                                            role='TRUST_ANCHOR')
 
    print('\nSending NYM request to the ledger')
    nym_transaction_response = await ledger.sign_and_submit_request(pool_handle=pool_handle,
                                                                    wallet_handle=steward_wallet,
                                                                    submitter_did=steward_did,
                                                                    request_json=nym_transaction_request)
    print("\nCreating professor wallet, DID, and master secret key")
    professor_wallet_config = json.dumps({"id": professor_id})
    professor_wallet_credentials = json.dumps({"key": professor_wallet_pass})
    try:
        await wallet.create_wallet(professor_wallet_config, professor_wallet_credentials)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    professor_wallet = await wallet.open_wallet(professor_wallet_config, professor_wallet_credentials)
    professor_did, professor_verkey = await did.create_and_store_my_did(professor_wallet, "{}")
    master_secret_id = await anoncreds.prover_create_master_secret(professor_wallet, professor_master_secr)
    
    print("\nCreating Authorization server wallet and DID")
    as_wallet_config = json.dumps({"id": as_id})
    as_wallet_credentials = json.dumps({"key": as_wallet_pass})
    try:
        await wallet.create_wallet(as_wallet_config, as_wallet_credentials)
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
    as_wallet = await wallet.open_wallet(as_wallet_config, as_wallet_credentials)
    await did.create_and_store_my_did(as_wallet, "{}")
    
    print('\nClosing wallet and pool')
    await wallet.close_wallet(steward_wallet)
    await wallet.close_wallet(professor_wallet)
    await wallet.close_wallet(aueb_wallet)
    await wallet.close_wallet(as_wallet)
    await pool.close_pool_ledger(pool_handle)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()


if __name__ == '__main__':
    main()
