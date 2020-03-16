from indy import did,wallet,crypto
import requests
import json
import asyncio
import base64
import datetime
import time

async def get_token():
    user = {
        'wallet_config': json.dumps({'id': 'user_wallet',"storage_config":{"path":"."}}),
        'wallet_credentials': json.dumps({'key': 'user_wallet_key'}),
        'did' : '4qk3Ab43ufPQVif4GAzLUW'
    }
    wallet_handle = await wallet.open_wallet(user['wallet_config'], user['wallet_credentials'])
    verkey = await did.key_for_local_did(wallet_handle, user['did'])
    nbf = time.mktime(datetime.datetime(2020, 4, 1, 00, 00).timetuple())
    exp = time.mktime(datetime.datetime(2020, 4, 1, 23, 59).timetuple()) 
    payload = {'did':user['did'], 'verkey': verkey, 'metadata':json.dumps({'aud': 'sofie-iot.eu','nbf':nbf, 'exp': exp})}
    response  = requests.post("http://localhost:9002/add", data = payload).text
    response =json.loads(response)
    print(response)
    await wallet.close_wallet(wallet_handle)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_token())
    loop.close()

if __name__ == '__main__':
    main()