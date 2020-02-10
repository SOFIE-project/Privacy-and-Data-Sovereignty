from http.server import BaseHTTPRequestHandler, HTTPServer
from indy import did,wallet,crypto
import cgi
import json
import random
import asyncio
import base64
import sys
import jwt

conf = {}

class Security:
    @staticmethod
    def create_nonce(length=30):
        return ''.join([str(random.randint(0, 9)) for i in range(length)])

class Indy:
    @staticmethod
    async def verify_did(client_did, challenge = None, signature=None, wallet_config = "", wallet_credentials=None, only_wallet_lookup=False, user_generated_challenge=False):
        if (client_did !=None and challenge == None):
            return 401, {'code':401, 'message': 'Proof required','challenge':Security.create_nonce()}
        if (client_did != None and challenge != None and signature != None and wallet_config!= None):
            wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
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
            await wallet.close_wallet(wallet_handle)
        else:
            return 403, {'code':403, 'message':'Invalide or missing input parameters'}


class PDS:
    @staticmethod
    def generate_token(private_key, audience=None):
        token = jwt.encode({'aud': 'sofie-iot.eu'},private_key, algorithm='RS256')
        return 200, {'code':200,'message':token.decode('utf-8')}
    
class PDSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global conf
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
            type  = form.getvalue("grant-type")
            grant = form.getvalue("grant")
            challenge = form.getvalue("challenge")
            proof = form.getvalue("proof")
            target = form.getvalue("target")
            if (type == "DID"):
                loop = asyncio.get_event_loop()
                code, output = loop.run_until_complete(
                    Indy.verify_did(grant, challenge, proof, json.dumps(conf['wallet_config']), json.dumps(conf['wallet_credentials']), True))
                if (code == 200):
                    with open(conf['as_private_key'], mode='rb') as file: 
                        as_private_key = file.read()
                    code, output = PDS.generate_token(as_private_key, target)
            self.send_response(code)
            self.send_header('Content-type','application/json'.encode())
            self.end_headers()
            self.wfile.write(json.dumps(output).encode())


def main():
    global conf
    if len(sys.argv) != 2:
        print ("Usage pds.py <configuration file>")
        sys.exit()
    with open(sys.argv[1]) as f:
        conf = json.load(f)
    httpd = HTTPServer(('localhost', conf["port"]), PDSHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    main()