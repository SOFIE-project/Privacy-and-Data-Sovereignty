from indy import anoncreds, crypto, did, ledger, pool, wallet
from indy.error import ErrorCode, IndyError
import json
import sys
import asyncio

pool_name             = 'SOFIE'
pool_genesis_txn_path = "/home/sofie/Indy_Testbed_Setup/config/SOFIE/pool_transactions_genesis"
aueb_trustee_id       = "aueb_trustee"
aueb_wallet_pass      = ""


async def run():
    try:
        print("\nConnecting to the pool")
        pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_path)})
        await pool.set_protocol_version(2)
        pool_handle = await pool.open_pool_ledger(pool_name, pool_config)

        print("\nOpening AUEB trustee wallet")
        aueb_wallet_config = json.dumps({"id": aueb_trustee_id})
        aueb_wallet_credentials = json.dumps({"key": aueb_wallet_pass})
        aueb_wallet = await wallet.open_wallet(aueb_wallet_config, aueb_wallet_credentials)
        aueb_dids = json.loads(await did.list_my_dids_with_meta(aueb_wallet))
        aueb_did =  aueb_dids[0]['did']

        print('\nBuild the SCHEMA request to add new schema to the ledger as a AUEB')
        (aueb_employee_schema_did, aueb_employee_schema) = await anoncreds.issuer_create_schema(aueb_did, 'AUEB-job-certificate', '1.2',
                                             json.dumps(['full_name', 'position']))
        schema_request = await ledger.build_schema_request(aueb_did, aueb_employee_schema)

        print('\nSending the SCHEMA request to the ledger')
        schema_response = await ledger.sign_and_submit_request(pool_handle, aueb_wallet, aueb_did, schema_request)

        print('\nCreating and storing CRED DEFINITION for the given Schema')
        (cred_def_id, cred_def_json) = await anoncreds.issuer_create_and_store_credential_def(aueb_wallet, aueb_did, aueb_employee_schema,'AUEBCERT1', 'CL', '{"support_revocation": false}')
        print ('\n******Copy and replace in the corresponding files the following code*****\n\n')
        print('cred_def_id = "' + cred_def_id + '"')
        print('cred_def_json = \'' + cred_def_json + '\'')
        print('schema_id = "' + aueb_employee_schema_did + '"')
        print('\n\n*****************************************************************************')
        cred_def_request = await ledger.build_cred_def_request(aueb_did, cred_def_json)
        await ledger.sign_and_submit_request(pool_handle, aueb_wallet, aueb_did, cred_def_request)
            
     
        print('\nClosing wallet and pool')
        await wallet.close_wallet(aueb_wallet)
        await pool.close_pool_ledger(pool_handle)
  
    except IndyError as e:
        print('Error occurred: %s' % e)



def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()


if __name__ == '__main__':
    main()
