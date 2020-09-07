from web3 import Web3
from rappor import Rappor

class Responder:
    def __init__(self):
        self.rappor = Rappor()
        w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
        self.account = w3.eth.accounts[0]
        survey_sc_address = "0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab"
        with open('conf/contract/build/survey.abi', 'r') as myfile:
            abi = myfile.read()
        self.surveyContract_instance = w3.eth.contract(abi = abi, address = survey_sc_address)

    def _generate_response(self, number_of_choices, correct_choice):
        response = self.rappor.permanent_randomized_response(number_of_choices, correct_choice)
        return response

    def record_response(self, number_of_choices, correct_choice, survey_name):
        response = self._generate_response(number_of_choices, correct_choice)
        self.surveyContract_instance.functions.recordResponses(survey_name, response).transact({'from': self.account})





