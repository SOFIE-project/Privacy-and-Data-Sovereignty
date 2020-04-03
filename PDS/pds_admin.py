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

conf = {}
wallet_handle = ""
pool_handle = ""

class PDSAdminHandler():
    def __init__(self):
        with open('conf/pds.conf') as f:
            self.conf = json.load(f)
        loop = asyncio.get_event_loop()
        self.wallet_handle = loop.run_until_complete(wallet.open_wallet(json.dumps(self.conf['wallet_config']), json.dumps(self.conf['wallet_credentials'])))
        self.pool_handle = None

    def wsgi_app(self, environ, start_response):
        req  = Request(environ)
        form = req.form
        code = 403
        output = {'code':403, 'message':'Invalide action'}
        action = form.get("action")
        ndid  = form.get("did","")
        verkey = form.get("verkey","")
        metadata = form.get("metadata","")
        if action == "add":
            if (ndid !=""):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                code, output = loop.run_until_complete(
                    Indy.add_did_to_wallet(self.wallet_handle, ndid, verkey, metadata))
        elif action == "get":
            if (ndid !=""):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                code, output = loop.run_until_complete(
                    Indy.get_did_metadata(self.wallet_handle, ndid))
        response = Response(json.dumps(output).encode(), status=code, mimetype='application/json')
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def create_app():
    app = PDSAdminHandler()
    return app

def main(): 
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 9002, app)


if __name__ == '__main__':
    main()