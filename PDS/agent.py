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
import base64  

conf={}

async def verify_did(client_did, challenge = None, signature=None, wallet_config = "", wallet_credentials=None, only_wallet_lookup=False, user_generated_challenge=False):
    if (client_did != None and challenge != None and signature != None and wallet_config!= None):
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        if (only_wallet_lookup):
            verkey = await did.key_for_local_did(wallet_handle, client_did)
        else:
            verkey = ""
        #Add code to check if verkey exists
        verification = await crypto.crypto_verify(verkey, challenge.encode(), base64.b64decode(signature))
        if(verification):
            print ("200")
            return 200
        else:
           print("403")
        await wallet.close_wallet(wallet_handle)
    else:
        print("403")

async def verify_proof(proof_req, proof):
    global conf
    schemas = json.dumps({conf['cred_schema_id']: json.loads(conf['cred_schema'])})
    cred_defs = json.dumps({conf['cred_def_id']: json.loads(conf['cred_def'])})
    verification = await anoncreds.verifier_verify_proof(proof_req,proof, schemas, cred_defs, "{}", "{}")
    if (verification):
        print ("200")
    else:
        print("401")

def main():
    global conf
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path+'/agent.conf') as f:
        conf = json.load(f)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--proof',   help="The proof")
    parser.add_argument('-r', '--request', help="The proof request")
    parser.add_argument('-v', '--verify',  help="Verifies a VC proof, use with -p -r", action='store_true')
    parser.add_argument('-d', '--did',  help="Verifies a DID using the request and the proof, use with -p -r", action='store_true')
    args = parser.parse_args()
    if(args.verify == True):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(verify_proof(args.request,args.proof))
        loop.close()
    if(args.did):
        wallet_config = conf['wallet_config']
        wallet_credentials = conf['wallet_credentials']
        loop = asyncio.get_event_loop()
        loop.run_until_complete(verify_did(args.did,args.request,args.proof, wallet_config, wallet_credentials, True))
        loop.close()


if __name__ == '__main__':
    main()
