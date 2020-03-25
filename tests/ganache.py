from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
with open('contract/PDS.abi', 'r') as myfile:
  abi = myfile.read()

with open('contract/PDS.bin', 'r') as myfile:
  binfile = myfile.read()
  bytecode = json.loads(binfile)['object']

account = w3.eth.accounts[0]
PDSContract = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = PDSContract.constructor().transact({'from': account})
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
address = tx_receipt.contractAddress
print(address)
PDSContract_instance = w3.eth.contract(abi=abi, address=address)
tx_hash = PDSContract_instance.functions.new_token('4qk3Ab43ufPQVif4GAzLUW', w3.toBytes(text='4qk3Ab43ufPQVif4GAzLUW')).transact({'from': account})
w3.eth.waitForTransactionReceipt(tx_hash)
DID, enc_token = PDSContract_instance.functions.get_token(0).call()
print(DID)