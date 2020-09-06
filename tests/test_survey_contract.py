import pytest
from web3 import Web3


@pytest.fixture(autouse=True, scope="class")
def Ganache():
    import subprocess
    import time
    global w3, surveyContract_instance, account

    p1 = subprocess.Popen(['ganache-cli', '-m', 'myth like bonus scare over problem client lizard pioneer submit female collect']) #use this mnemonic to much the contract address in configuration
    time.sleep(10)

    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))

    with open('conf/contract/build/survey.bin', 'r') as myfile:
        binfile = myfile.read()
    with open('conf/contract/build/survey.abi', 'r') as myfile:
        abi = myfile.read()
    
    account = w3.eth.accounts[0]
    surveyContract = w3.eth.contract(abi=abi, bytecode=binfile)
    tx_hash = surveyContract.constructor().transact({'from': account})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    address = tx_receipt.contractAddress
    
    surveyContract_instance = w3.eth.contract(abi = abi, address = address)
    survey_name = "test"
    number_of_questions = 2
    tx_hash = surveyContract_instance.functions.createSurvey(survey_name, number_of_questions).transact({'from': account})

    yield
    p1.kill()

class TestSurveyContract:
    def test_survey_creation(self):
        global w3, surveyContract_instance, account

        survey_name = "test"
        number_of_questions = 2
        tx_hash = surveyContract_instance.functions.createSurvey(survey_name, number_of_questions).transact({'from': account})

        number_of_questions1 = surveyContract_instance.functions.getNumberOfQuestions(survey_name).call()
        
        assert(number_of_questions == number_of_questions1)

    def test_responses(self):
        global w3, surveyContract_instance, account

        survey_name = "test"
        responses = [1,0]
        tx_hash = surveyContract_instance.functions.recordResponses(survey_name, responses).transact({'from': account})

        counter = surveyContract_instance.functions.getCounter(survey_name).call()
        responses_question1 = surveyContract_instance.functions.getResponses(survey_name, 0).call()
        responses_question2 = surveyContract_instance.functions.getResponses(survey_name, 1).call()


        assert(counter == 1 and responses_question1 == 1 and responses_question2 == 0)

    def test_reset_survey(self):
        global w3, surveyContract_instance, account

        survey_name = "test"
        responses = [1,0]
        tx_hash = surveyContract_instance.functions.recordResponses(survey_name, responses).transact({'from': account})

        tx_hash1 = surveyContract_instance.functions.resetSurvey(survey_name).transact({'from': account})

        counter = surveyContract_instance.functions.getCounter(survey_name).call()
        responses_question1 = surveyContract_instance.functions.getResponses(survey_name, 0).call()
        responses_question2 = surveyContract_instance.functions.getResponses(survey_name, 1).call()

        assert(counter == 0 and responses_question1 == 0 and responses_question2 == 0)
