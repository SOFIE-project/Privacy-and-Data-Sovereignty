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

with open('./agent.conf') as f:
    conf = json.load(f)

async def verify_proof(proof_req, proof):
    schemas = json.dumps({conf['cred_schema_id']: json.loads(conf['cred_schema'])})
    cred_defs = json.dumps({conf['cred_def_id']: json.loads(conf['cred_def'])})
    verification = await anoncreds.verifier_verify_proof(proof_req,proof, schemas, cred_defs, "{}", "{}")
    if (verification):
        print ("200")
    else:
        print("401")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--proof',   help="The proof")
    parser.add_argument('-r', '--request', help="The proof request")
    parser.add_argument('-v', '--verify',  help="Verifies a proof, use with -p -r", action='store_true')
    args = parser.parse_args()
    if(args.verify == True):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(verify_proof(args.request,args.proof))
        loop.close()


if __name__ == '__main__':
    main()
