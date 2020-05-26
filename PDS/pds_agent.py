from indy import did,wallet,crypto
import requests
import json
import asyncio
import base64

class PDS_agent:
    @staticmethod
    async def get_token_from_did(pds_url, user_did, target, wallet_config, wallet_credentials):
        payload = {'grant-type':'DID', 'grant':user_did, 'target': target}
        response  = requests.post(pds_url +"/gettoken", data = payload).text
        response =json.loads(response)
        challenge = response['challenge']
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        verkey = await did.key_for_local_did(wallet_handle, user_did)
        signature = await crypto.crypto_sign(wallet_handle, verkey, challenge.encode())
        signature64 = base64.b64encode(signature)
        payload = {'grant-type':'DID', 'grant':user_did, 'challenge': challenge, 'proof':signature64, 'target': target}
        response  = requests.post(pds_url +"/gettoken", data = payload).text
        response =json.loads(response)
        await wallet.close_wallet(wallet_handle)
        return response['message']
