from werkzeug.wrappers import Request, Response
from indy import did,wallet,crypto
from indy_agent import Indy
import cgi
import json
import random
import asyncio
import base64
import sys
import jwt

class PDS:
    def __init__(self, wallet_handle, pool_handle):
        self.wallet_handle = wallet_handle
        self.pool_handle = pool_handle

    def generate_token(self, private_key, audience=None,  subject=None, expires=None, token_type=None ):
        claims = {}
        if audience:
            claims['aud'] = audience
        if subject:
            claims['sub'] = subject
        if expires:
            claims['exp'] = expires
        token = jwt.encode(claims,private_key, algorithm='RS256')
        if token_type == None:
            return 200, {'code':200,'message':token.decode('utf-8')}
        if token_type == "DID-encrypted":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            code, output = loop.run_until_complete(
                Indy.encrypt_for_did(subject, token.decode('utf-8'), self.wallet_handle, self.pool_handle, True)
            )
            loop.close()
            return code, output


class PDSHandler():
    def __init__(self):
        with open('conf/pds.conf') as f:
            self.conf = json.load(f)
        loop = asyncio.get_event_loop()
        self.wallet_handle = loop.run_until_complete(wallet.open_wallet(json.dumps(self.conf['wallet_config']), json.dumps(self.conf['wallet_credentials'])))
        self.pool_handle = None
        self.pds = PDS(self.wallet_handle, self.pool_handle)

    def wsgi_app(self, environ, start_response):
        req  = Request(environ)
        form = req.form
        code = 403
        output = {'code':403, 'message':'Invalide or missing input parameters'}

        grant_type  = form.get("grant-type", None)
        grant       = form.get("grant", None)
        challenge   = form.get("challenge", None)
        proof       = form.get("proof", None)
        target      = form.get("target", None)
        token_type  = form.get("token-type", None)
        subject     = form.get("subject", None)
        log_token   = form.get("log-token", False)
        expires     = form.get("expires", None)
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
        if (grant_type == "auth_code"):
            code = 200
        if (code == 200):
            with open(self.conf['as_private_key'], mode='rb') as file: 
                as_private_key = file.read()
            code, output = self.pds.generate_token(as_private_key, target, subject, expires, token_type)

        response = Response(json.dumps(output).encode(), status=code, mimetype='application/json')
        return response(environ, start_response)
    
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def create_app():
    app = PDSHandler()
    return app

def main(): 
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('', 9001, app)


if __name__ == '__main__':
    main()