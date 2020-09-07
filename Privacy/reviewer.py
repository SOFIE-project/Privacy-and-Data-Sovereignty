from web3 import Web3

class Reviewer:
    def __init__(self):
        w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
        self.account = w3.eth.accounts[0]
        survey_sc_address = "0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab"
        with open('conf/contract/build/survey.abi', 'r') as myfile:
            abi = myfile.read()
        self.surveyContract_instance = w3.eth.contract(abi = abi, address = survey_sc_address)

    def _estimate_responses(self, responses, total_responders):
        estimations = [0] * len(responses)
        for x in range(len(responses)):
            propability = max(0, 2*(responses[x]/total_responders - 0.25))
            estimations[x]   = propability
        return estimations

    def estimate_responses(self, number_of_choices, survey_name):
        total_responders = self.surveyContract_instance.functions.getCounter(survey_name).call()
        responses = self.surveyContract_instance.functions.getResponses(survey_name).call()
        return self._estimate_responses(responses, total_responders)








