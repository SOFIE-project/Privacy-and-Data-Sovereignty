import requests
from indy import anoncreds, crypto, did, ledger, pool, wallet
from indy.error import ErrorCode, IndyError
import json
import sys
import asyncio
import os
import argparse


with open('client.conf') as f:
    conf = json.load(f)
pool_name             = conf['pool_name']
pool_genesis_txn_path = os.getcwd()+ conf['pool_genesis_txn_path']

user = conf['user']

async def get_token(as_url, aud="", sub=""):
    post_data = {'grant_type':'verifiable_credentials'}
    proof_req  = requests.post(as_url, data = post_data).text
    print("<---------")
    print ("Received proof request: " + proof_req)
    proof = await generate_proof(proof_req)
    print("--------->")
    print ("Will respond with: " + proof)
    post_data.update({'proof':proof})
    if aud:
        post_data.update({'aud':aud})
    if sub:
        post_data.update({'sub':sub})
    token  = requests.post(as_url, data = post_data).text
    print("<---------")
    print ("Received token: " + token)

async def generate_proof(proof_req):
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    prover_cred_search_handle = await anoncreds.prover_search_credentials_for_proof_req(wallet_handle, proof_req, None)
    creds_for_attr1 = await anoncreds.prover_fetch_credentials_for_proof_req(prover_cred_search_handle,'attr1_referent', 1)
    prover_cred_for_attr1 = json.loads(creds_for_attr1)[0]['cred_info']
    await anoncreds.prover_close_credentials_search_for_proof_req(prover_cred_search_handle)
    prover_requested_creds = json.dumps({
            'self_attested_attributes': {},
            'requested_attributes': {
                'attr1_referent': {
                    'cred_id': prover_cred_for_attr1['referent'],
                    'revealed': True
                }
            },
            'requested_predicates': {}
        })
    schemas = json.dumps({conf['cred_schema_id']: json.loads(conf['cred_schema'])})
    cred_defs = json.dumps({conf['cred_def_id']: json.loads(conf['cred_def'])})
    proof = await anoncreds.prover_create_proof(wallet_handle, proof_req, prover_requested_creds, user['msk'], schemas, cred_defs, "{}")
    return proof                                                                         


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--authorize', type=str, help="Receive token from the provided authorisation server")
    parser.add_argument('-t', '--target', type=str, help="The aud field of the JWT", default="")
    parser.add_argument('-s', '--sub', type=str, help="The sub field of the JWT", default="")
    args = parser.parse_args()
    if (args.authorize):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(get_token(args.authorize, args.target, args.sub))
        loop.close()

if __name__ == '__main__':
    main()
