# Privacy and Data Sovereignty Component
## Description


### Architecture Overview



### Relation with SOFIE

Nore information about this compoment and its relation to the SOFIE project can be found in [D2.5 Federation Framework, SOFIE deliverable](https://media.voog.com/0000/0042/0957/files/SOFIE_D2.5-Federation_Framework%2C_2nd_version.pdf)


### Key Technologies



## Usage


## Installation

### Prerequisites
Python 3, Hyperledger Indy SDK and the python wrapper, PyJWT are required. Use the following commands to install the prerequisites in Ubuntu 18.04 

* sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
* sudo add-apt-repository "deb https://repo.sovrin.org/sdk/deb bionic stable"
* sudo apt-get update
* sudo apt-get install -y libindy
* pip3 install python3-indy pyjwt web3
* pip3 install Werkzeug


### Configuration
A sample configuration file is provided at conf/psd.conf


### Execution from source
From the root directory run `python3 PDS/pds.py`

### Dockerized version
In order to build PDS image, execute the script `docker-build.sh`. Then you can run PDS using, for example,  `docker run -tid --rm -p 9001-9002:9001-9002 pds`. You can verify that PDS is running properly be executing in the examples folder: `python3 get_token.py`

### Usage
The executed script creates an HTTP server that listens for REST API calls at port 9001. The REST API of PDS component is documented in 

https://app.swaggerhub.com/apis-docs/nikosft/SOFIE-PDS-IAA/1.0.0#/PDS/gettoken 

Please select **schema** to see all available API parameters and their documentation.


## Testing

### Prerequisites
For testing purposes ganache-cli and Indy testing pool are required. To install ganache execute:

* npm install -g ganache-cli

To install Indy testing pool, execute from the component's root folder:

* docker build -f tests/conf/indy-pool.dockerfile -t indy_pool . 

Tests are executed using pytest and pytest-asyncio. To install it execute 

* pip3 install -U pytest 
* pip3 install pytest-asyncio

### Running the tests
First you need to run Hyperledger Indy testing pool:

* docker run --name test_pool -itd --rm -p 9701-9708:9701-9708 indy_pool

Then you need to setup Indy testing accounts, and finally run the test. From the root directory run:

* python3 tests/indy_setup.py 
* python3 -m pytest -s  tests/


## Integration

To be provided.

## Deployment

To be provided.

## Known/Open Issues

No known issues

## Contact info

Please contact Nikos Fotiou or Dimitris Dimopoulos (AUEB) in case of any questions.

***