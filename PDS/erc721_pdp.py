import jwt
import json
from web3 import Web3

class ERC721_pdp:
    def __init__(self):
        with open('conf/erc721.conf') as f:
            self.conf = json.load(f)
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.conf['web3provider']))
            with open('conf/contract/build/ERC721Metadata.abi', 'r') as myfile:
                self.abi = myfile.read()
            self.ERC721Contract_instance = self.w3.eth.contract(abi=self.abi, address=Web3.toChecksumAddress(self.conf['iaa_sc_address']))
        except:
            print("Couldn't connect to Ethereum blockchain:" + self.conf['web3provider'])
            pass

    def record_erc721(self):
        print("recoreding")