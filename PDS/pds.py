from http.server import BaseHTTPRequestHandler, HTTPServer
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

class PDS:
    @staticmethod
    def generate_token(private_key, audience=None,  subject=None, token_type=None ):
        token = jwt.encode({'aud': 'sofie-iot.eu'},private_key, algorithm='RS256')
        if token_type == None:
            return 200, {'code':200,'message':token.decode('utf-8')}
        if token_type == "DID-encrypted":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            code, output = loop.run_until_complete(
                Indy.encrypt_for_did(subject, token.decode('utf-8'),wallet_handle,pool_handle, True)
            )
            loop.close()
            return code, output


class PDSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        path = self.path
        if path == "/gettoken":
            code = 403
            output = {'code':403, 'message':'Invalide or missing input parameters'}
            form = cgi.FieldStorage(
                fp = self.rfile, 
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE':self.headers['Content-Type'],
                        })
            grant_type  = form.getfirst("grant-type", None)
            grant       = form.getfirst("grant", None)
            challenge   = form.getfirst("challenge", None)
            proof       = form.getfirst("proof", None)
            target      = form.getfirst("target", None)
            token_type  = form.getfirst("token-type", None)
            subject     = form.getfirst("subject", None)
            log_token   = form.getfirst("log-token", False)
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
                    Indy.verify_did(grant, challenge, proof, wallet_handle,pool_handle, True))
                loop.close()
            if (grant_type == "auth_code"):
                code = 200
            if (code == 200):
                with open(conf['as_private_key'], mode='rb') as file: 
                    as_private_key = file.read()
                code, output = PDS.generate_token(as_private_key, target, subject, token_type)
            self.send_response(code)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps(output).encode())

def main():
    global conf
    global wallet_handle
    global pool_handle
    if len(sys.argv) != 2:
        print ("Usage pds.py <configuration file>")
        sys.exit()
    with open(sys.argv[1]) as f:
        conf = json.load(f)
    httpd     = HTTPServer(('', conf["port"]), PDSHandler)
    loop = asyncio.get_event_loop()
    wallet_handle = loop.run_until_complete(wallet.open_wallet(json.dumps(conf['wallet_config']), json.dumps(conf['wallet_credentials'])))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    loop.run_until_complete(wallet.close_wallet(wallet_handle))


if __name__ == '__main__':
    main()