# Privacy and Data Sovereignty Component
## Description

The Privacy and Data Sovereignty (PDS) component provides mechanisms that allow actors to better control their data, as well as mechanisms that protect clients’ privacy.

In its present form, this component extends the IAA component in the following ways: (i) it enables flexible authorisation server delegation, and (ii) it enables client authentication and authorisation using verifiable credentials (VCs).

### Architecture Overview

The PDS component is composed of 5 sub-scomponents: Client, Smart contracts, IAA blockchain agent, Authorization Server, and IoT platform.

#### Client
This this sub-component includes libraries that can be used by an external client application in order to access a platform using the PDS component. 

#### Smart contracts
The PDS component currently includes a single Ethereum smart contract which manages the “access control delegation” functionality of the component. The principal operation of this smart contract is that it allows resource owners to register the addresses of the authorisation servers that are responsible for managing their resources

#### PDS blockchain agent
Similarly to the [IAA component](https://github.com/SOFIE-project/IAA), this sub-component includes a blockchain agent entity that mediates the communication between the authorisation server (see next), the authorisation delegation smart contract, and the Hyperledger Indy pool

#### Authorization server
This entity is an enhanced version of the [OAuth2 php server](https://github.com/bshaffer/oauth2-server-php). It supports verfiable credentials and access control delegation. 

### IoT platform
A sample IoT platform used for testing pursposed. 


### Relation with SOFIE

Nore information about this compoment and its relation to the SOFIE project can be found in [D2.5 Federation Framework, SOFIE deliverable](https://media.voog.com/0000/0042/0957/files/SOFIE_D2.5-Federation_Framework%2C_2nd_version.pdf)


### Key Technologies

The following table includes the key technologies used for each sub-component

| Sub-component | Technologies |
| ------------- | ------------- |
| Client  | Hyper Ledger Indy python SDK |
| Smart contracts  | Solidity  |
| PDS blockchain agent  | Hyper Ledger Indy pyhton SDK   |
| Authorization server  | php compatilbe web server, OAuth2 |


## Usage


## Installation

### Prerequisites

#### Client
Python 3 is required

#### Smart contracts
Smart contracts should be installed in an Ethereum network. 

#### PDS blockchain agent
Python 3 is required 

#### Authorization server
The Authorization-server fodler should be stored in a web server that supports php and python 3, so it can be accessed over HTTP(s) (NOTE accessing the Authorization server is not secure).

### Configuration

The setup folder contains some setup scripts that must be run only once. These scipts set up the pool, the corresponding wallets, and DIDs. These scripts assume an existing pool of Indy nodes. Moreover, these scripts require Indy-SDK. In all python files replace the variables pool_name and pool_genesis_txn_path with the correct values. Edit the file setup/1.setup_pool_and_wallets.py and modify the variables steward_id, steward_seed and steward_conf_did accordingly. Then run this scipt.

As a next step run the script setup/2.create_schema_and_credentials.py This script will output some python code. This code should be tranferred to the following files: setup/3.issue_credentials.py, Clinet/client.py and Agent/PDS-DIDagent.py.

Finally, execute the script setup/3.issue_credentials.py


## Testing

To be provided 


## Integration

To be provided.

## Deployment

To be provided.

## Known/Open Issues

No known issues

## Contact info

Please contact Nikos Fotiou or Dimitris Dimopoulos (AUEB) in case of any questions.

***