from indy import did,wallet,crypto
import requests
import json
import asyncio
import base64

async def get_token():
    user = {
        'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"."}}),
        'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
        'did' : '4qk3Ab43ufPQVif4GAzLUW'
    }
    payload = {'grant-type':'DID', 'grant':user['did'], 'target':"sofie-iot.eu"}
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    challenge = response['challenge']
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    signature = await crypto.crypto_sign(wallet_handle, verkey, challenge.encode())
    signature64 = base64.b64encode(signature)
    payload = {'grant-type':'DID', 'grant':user['did'], 'challenge': challenge, 'proof':signature64, 'target':'sofie-iot.eu'}
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    print(response)
    await wallet.close_wallet(wallet_handle)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_token())
    loop.close()

if __name__ == '__main__':
    main()