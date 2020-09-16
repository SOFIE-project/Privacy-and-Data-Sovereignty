from werkzeug.wrappers import Request, Response
from indy import did,wallet,crypto
from indy_agent import Indy
from web3 import Web3
from pds_admin import PDSAdminHandler
from erc721_pdp import ERC721_pdp
import cgi
import json
import random
import asyncio
import base64
import sys
import jwt
import nacl.encoding
from nacl.public import SealedBox

class PDS:
    def __init__(self, wallet_handle=None, pool_handle=None):
        self.wallet_handle = wallet_handle
        self.pool_handle = pool_handle

    def generate_token(self, private_key, metadata = None, enc_key=None, token_type=None ):
        claims = {}
        metadata = json.loads(metadata)
        #create token_id
        if 'aud' in metadata:
            claims['aud'] = metadata['aud']
        if 'sub' in metadata:
            claims['sub'] = metadata['sub']
        if 'exp' in metadata:
            claims['exp'] = metadata['exp']
        if 'nbf' in metadata:
            claims['nbf'] = metadata['nbf']
        claims['jti'] = random.getrandbits(256)
        token = jwt.encode(claims,private_key, algorithm='RS256')
        if enc_key:
            public_key = nacl.public.PublicKey(enc_key,nacl.encoding.HexEncoder)
            sealed_box = SealedBox(public_key)
            token = sealed_box.encrypt(token)
            token = base64.urlsafe_b64encode(token)
        #return 200, {'code':200,'message':token.decode('utf-8')}
        return token, claims

    
    def log_token(self, metadata, logged_token, web3_provider, eth_account, PDSContract_instance):
        #tx_hash = PDSContract_instance.functions.new_token(web3_provider.toBytes(text=metadata), web3_provider.toBytes(text=logged_token)).transact({'from': eth_account})
        tx_hash = PDSContract_instance.functions.new_token(metadata, web3_provider.toBytes(text=logged_token)).transact({'from': eth_account})
        web3_provider.eth.waitForTransactionReceipt(tx_hash)
        return 200, {'code':200,'message':'token logged'}

class PDSHandler():
    def __init__(self):
        with open('conf/pds.conf') as f:
            self.conf = json.load(f)
        loop = asyncio.get_event_loop()
        self.wallet_handle = loop.run_until_complete(wallet.open_wallet(json.dumps(self.conf['wallet_config']), json.dumps(self.conf['wallet_credentials'])))
        self.pool_handle = None
        self.erc721_pdp = ERC721_pdp()
        try:
            self.pds = PDS(self.wallet_handle, self.pool_handle)
            self.web3_provider = Web3(Web3.HTTPProvider(self.conf['web3provider']))
            self.eth_account = self.web3_provider.eth.accounts[0]
            with open('conf/contract/build/PDS.abi', 'r') as myfile:
                self.abi = myfile.read()
            self.PDSContract_instance = self.web3_provider.eth.contract(abi=self.abi, address=Web3.toChecksumAddress(self.conf['pds_sc_address']))
        except:
            print("Couldn't connect to Ethereum blockchain:" + self.conf['web3provider'])
            pass

    def wsgi_app(self, environ, start_response):
        req  = Request(environ)
        form = req.form
        code = 403
        output = {'code':403, 'message':'Invalide or missing input parameters'}

        grant_type        = form.get("grant-type", None)
        grant             = form.get("grant", None)
        challenge         = form.get("challenge", None)
        proof             = form.get("proof", None)
        token_type        = form.get("token-type", None)
        log_token         = form.get("log-token", None)
        enc_key           = form.get("enc-key", None)
        record_erc721     = form.get("erc-721", None)

        if (grant_type == "DID"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            '''
            print("POST parameters:")
            print(grant)
            print(challenge)
            print(proof)
            print(token_type)
            print(subject)
            '''
            code, output = loop.run_until_complete(
                Indy.verify_did(grant, challenge, proof, self.wallet_handle, self.pool_handle, True))
            loop.close()
            if code == 200:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                _, output = loop.run_until_complete(
                    Indy.get_did_metadata(self.wallet_handle, grant))
                metadata  = output['message']
        if (grant_type == "auth_code"):
            metadata  = form.get("metadata", None)
            code = 200
        if (code == 200):
            with open(self.conf['as_private_key'], mode='rb') as file: 
                as_private_key = file.read()
            token,claims = self.pds.generate_token(as_private_key, metadata, enc_key)
            output = {'code':200,'message':token.decode('utf-8')}
            if (log_token):
                self.pds.log_token(log_token, output['message'], self.web3_provider,self.eth_account, self.PDSContract_instance)
                print("token logged")
            if (record_erc721):
                self.erc721_pdp.record_erc721(self.eth_account, claims['jti'], output['message'])
                print("Creating ERC-721 token")
        response = Response(json.dumps(output).encode(), status=code, mimetype='application/json')
        return response(environ, start_response)
    
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def create_app():
    app = PDSHandler()
    return app

def create_admin_app(wallet_handle = None):
    app = PDSAdminHandler(wallet_handle)
    return app

def main(): 
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('', 9001, app)


if __name__ == '__main__':
    main()