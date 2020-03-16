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

class PDSAdminHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        path = self.path
        if path == "/add":
            code = 403
            output = {'code':403, 'message':'Invalide or missing input parameters'}
            form = cgi.FieldStorage(
                fp = self.rfile, 
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE':self.headers['Content-Type'],
                        })
            ndid  = form.getfirst("did","")
            verkey = form.getfirst("verkey","")
            metadata = form.getfirst("metadata","")
            if (ndid !=""):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                code, output = loop.run_until_complete(
                    Indy.add_did_to_wallet(wallet_handle, ndid, verkey, metadata))
            self.send_response(code)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps(output).encode())
        if path == "/get":
            code = 403
            output = {'code':403, 'message':'Invalide or missing input parameters'}
            form = cgi.FieldStorage(
                fp = self.rfile, 
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE':self.headers['Content-Type'],
                        })
            ndid  = form.getfirst("did","")
            if (ndid !=""):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                code, output = loop.run_until_complete(
                    Indy.get_did_metadata(wallet_handle, ndid))
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
    httpadmin = HTTPServer(('', conf["adminport"]), PDSAdminHandler)
    loop = asyncio.get_event_loop()
    wallet_handle = loop.run_until_complete(wallet.open_wallet(json.dumps(conf['wallet_config']), json.dumps(conf['wallet_credentials'])))
    
    try:
        httpadmin.serve_forever()
    except KeyboardInterrupt:
        pass
    httpadmin.server_close()
  
    loop.run_until_complete(wallet.close_wallet(wallet_handle))


if __name__ == '__main__':
    main()