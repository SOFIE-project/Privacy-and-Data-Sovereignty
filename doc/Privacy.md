# Privacy Module
## Description
This is the documentation for the Privacy module of SOFIE's PDS component. The module provides
a smart contract that collects responses to "surveys". The responses include noise generated
using Local Differential Privacy

## Key technologies
In order to provide local differential privacy the module implements the basic one-time RAPPOR algorithm, described
in 

> U. Erlingsson, V. Pihur, and A. Korolova, “RAPPOR: Randomized
Aggregatable Privacy-Preserving Ordinal Response,” in Proc. of ACM
SIGSAC Conference on Computer and Communications Security, 2014

## Installation

### Prerequisites
Python 3 the web3 library are required. Web3 can be installed Ubuntu 18.04 using

* pip3 install web3

## Usage

Before using this module a "survey" must be created. Each survey is composed by a single question that has multiple possible answers (multiple choice question). 
A survey is created by invoking the `createSurvey` function of the 
smart contract. This function accepts two inputs: the survey `name` and the number of choices (`numberOfQuestions`).
The content of the question and the semantics of the choices are application specific and are not stored in the contract.

A user can privately respond to a survey by using the `Responder` class included in the `responder.py` file. This class implements
a method called `record_response`. This method accepts the following inputs:

| Parameter | Meaning |
| --- | --- |
| number_of_choices | (int) The number of possible choices to the question|
| correct_choice | (int  in the range of [0, number_of_choices)) the correct choice |
| survey_name | (string) the name of the survey |

This method generated a privacy preserving response and stored it in the smart contract. 

If a significant number of responses has been collected(~1000) then statistics with quite good precision can be collected. The class `Reviewer`
implemented in the `reviewer.py` file, provides a method (`estimate_responses`) that generates the probability of each choice, based on the information 
recorded in the smart contact.  This method accepts the following inputs:

| Parameter | Meaning |
| --- | --- |
| number_of_choices | (int) The number of possible choices to the question|
| survey_name | (string) the name of the survey | 

It returns an array of size `number_of_choices` and each element of the array is the probability of the corresponding choice

## Contact info

Please contact Nikos Fotiou or Iakovos Pittaras (AUEB) in case of any questions.

***