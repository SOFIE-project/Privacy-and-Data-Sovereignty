from indy import did,wallet,crypto
import asyncio
import base64
import random
import json

class Indy:
    @staticmethod
    def create_nonce(length=30):
        return ''.join([str(random.randint(0, 9)) for i in range(length)])

    @staticmethod
    async def add_did_to_wallet(wallet_handle, ndid, verkey="", metadata=""):
        await did.store_their_did(wallet_handle,json.dumps({"did": ndid, "verkey": verkey}))
        await did.set_did_metadata(wallet_handle, ndid, metadata)
        return 200, {'code':200,'message':'Success'}

    @staticmethod
    async def get_did_metadata(wallet_handle, ndid):
        metadata = await did.get_did_metadata(wallet_handle, ndid)
        return 200, {'code':200,'message':metadata}

    @staticmethod
    async def encrypt_for_did(client_did, message, wallet_handle="", pool_handle="", only_wallet_lookup=False):
        if (client_did != None and wallet_handle!= None):
            if (only_wallet_lookup):
                verkey = await did.key_for_local_did(wallet_handle, client_did)
            else:
                verkey = ""
            #Add code to check if verkey exists
        enc = await crypto.anon_crypt(verkey, message.encode())
        return 200, {'code':200,'message': base64.urlsafe_b64encode(enc).decode()}

    @staticmethod
    async def verify_did(client_did, challenge = None, signature=None, wallet_handle="", pool_handle="", only_wallet_lookup=False, user_generated_challenge=False):
        if (client_did !=None and challenge == None):
            return 401, {'code':401, 'message' : 'Proof required','challenge': Indy.create_nonce()}
        if (client_did != None and challenge != None and signature != None and wallet_handle!= None):
            if (only_wallet_lookup):
                verkey = await did.key_for_local_did(wallet_handle, client_did)
            else:
                verkey = ""
            #Add code to check if verkey exists
            verification = await crypto.crypto_verify(verkey, challenge.encode(), base64.b64decode(signature))
            if(verification):
                return 200, {'code':200,'message':'Success'}
            else:
                return 403, {'code':403, 'message':'Signature verification failed'}
        else:
            return 403, {'code':403, 'message':'Invalide or missing input parameters'}