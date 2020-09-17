from indy import did,wallet,crypto, anoncreds
import asyncio
import base64
import random
import json

class Indy_pdp:
    def __init__(self):
        try:
            with open('conf/indy.conf') as f:
                self.conf = json.load(f)
            self.wallet_handle = asyncio.get_event_loop().run_until_complete(
                wallet.open_wallet(json.dumps(self.conf['wallet_config']), json.dumps(self.conf['wallet_credentials'])))
            self.pool_handle = None
        except:
            print("Couldn't initiate Hyperledger Indy PDP")
            pass

    def create_nonce(self, length=30):
        return ''.join([str(random.randint(0, 9)) for i in range(length)])


    def get_did_metadata(self, ndid):
        metadata = asyncio.get_event_loop().run_until_complete(
            did.get_did_metadata(self.wallet_handle, ndid))
        return metadata


    def verify_did(self, client_did, challenge = None, signature=None, only_wallet_lookup=False, user_generated_challenge=False):
        if (client_did !=None and challenge == None):
            return 401, self.create_nonce()
        if (client_did != None and challenge != None and signature != None and self.wallet_handle!= None):
            if (only_wallet_lookup):
                verkey = asyncio.get_event_loop().run_until_complete(
                    did.key_for_local_did(self.wallet_handle, client_did))
            else:
                verkey = ""
            #Add code to check if verkey exists
            verification = asyncio.get_event_loop().run_until_complete(
                crypto.crypto_verify(verkey, challenge.encode(), base64.b64decode(signature)))
            if(verification):
                return 200, self.get_did_metadata(client_did)
            else:
                return 403, 'Signature verification failed'
        else:
            return 403, 'Invalide or missing input parameters'
