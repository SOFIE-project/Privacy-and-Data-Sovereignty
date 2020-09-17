import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../PDS/')

import pytest
import requests
import json
import base64
import datetime
import time
import jwt

@pytest.fixture(autouse=True, scope="module")
def server():
    import subprocess
    import time
    p1 = subprocess.Popen(['python3', 'PDS/pds.py'])
    time.sleep(5) #Otherwise the server is not ready when tests start
    yield
    p1.kill()


def test_valid_auth_code():
    nbf = time.mktime(datetime.datetime(2020, 4, 1, 00, 00).timetuple())
    exp = time.mktime(datetime.datetime(2020, 4, 1, 23, 59).timetuple()) 
    payload = {'grant-type':'auth_code', 'grant':'shared_secret_key', 'metadata':json.dumps({'aud': 'sofie-iot.eu','nbf':nbf, 'exp': exp})}
    response  = requests.post("http://localhost:9001/gettoken", data = payload).text
    response =json.loads(response)
    token = response['message']
    print(token)
    assert(response['code'] == 200 ) 

