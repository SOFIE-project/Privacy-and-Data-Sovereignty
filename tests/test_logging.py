import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../PDS/')

import pytest
import asyncio
import json
import base64

from web3 import Web3
from pds import PDS

@pytest.fixture(autouse=True, scope="module")
def deploy_ganache():
    import subprocess
    import time
    global w3, abi, account, address
    p1 = subprocess.Popen(['ganache-cli', '-m', 'myth like bonus scare over problem client lizard pioneer submit female collect']) #use this mnemonic to much the contract address in configuration
    time.sleep(10) #Otherwise the server is not ready when tests start
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
    with open('conf/contract/build/PDS.abi', 'r') as myfile:
        abi = myfile.read()
    with open('conf/contract/build/PDS.bin', 'r') as myfile:
        binfile = myfile.read()
    account = w3.eth.accounts[0]
    PDSContract = w3.eth.contract(abi=abi, bytecode=binfile)
    tx_hash = PDSContract.constructor().transact({'from': account})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    address = tx_receipt.contractAddress
    yield
    p1.kill()

@pytest.mark.asyncio
async def test_log_token():
    global w3, abi, account, address
    pds = PDS()
    logged_token = 'Od7Fsc5Z68fSaC4PNu0t1eXYr8tI7no28aXjCEypjxjohc0PwkItlVTjCduAOwlwg3gtIdcSXufv5WYuowoV9Hak8yWMy_74SZe06Fs4DfrMRDJZsAXSYac08tmTvu440VkXfZwZ7NouoQbZgMCzPL6jxKWwV2hN06ti4GCFRR6TbymgZeFroeTH3WT9iM-Lo1mtr0bWsH93qsXIlHK0IOaMwskjPJHSKwOoFIW84DFHSHY0TdUn8U_fKz55oEwd5x5WyHeu_OVVqO03GgToZN_tPp_6vjxDPtwzHZYRmiYX08oWKotHAPGloqyMmt3MHOlwag1YFHcxMvHx0Gw9t6NUHRMhU3J9EEhE4UgS6Ol-G9ea-qeCRc_WEzgMukjfxb-wGfPCRFlNyYOJt1XxI2whTbKj_wao0kN17NHIT6suFPEDnW7DBsyYEG8cXO5MLzKkDplLSVnet7xTWMmnPlm6yR8hwXeE0MHjpWeLu0Lw-uJ6aKu2fVla-aaD8d6w05MFURsgiUwjjSf7omlABeuI6KCQWO_rTqSPZ4yx7e7GO7YY4cvpw1IxK1jbxHVaY-8dCHyXyDCUhBXvfGJXHJx--n-KyLVo7tXy5dbd2j4K8-MD0EDTPmbar8OBnlyKO5rG9PqWOjEkEcu8t-WfGpbTcw=='
    logged_did = '4qk3Ab43ufPQVif4GAzLUW'
    PDSContract_instance = w3.eth.contract(abi=abi, address=address)
    code, result = pds.log_token(logged_did, logged_token, w3, account, PDSContract_instance)
    DID, enc_token = PDSContract_instance.functions.get_token(0).call()
    assert (DID != None)
    assert (enc_token != None)