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
                    Indy.verify_did(grant, challenge, proof, wallet_handle,pool_handle, True))
                if (code == 200):
                    with open(conf['as_private_key'], mode='rb') as file: 
                        as_private_key = file.read()
                    code, output = PDS.generate_token(as_private_key, target)
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
    httpd = HTTPServer(('', conf["port"]), PDSHandler)
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