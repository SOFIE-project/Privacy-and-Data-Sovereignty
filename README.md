# Privacy and Data Sovereignty Component
## Description
This is the Privacy and Data Sovereignty (PDS) Component of the [SOFIE framework](https://github.com/SOFIE-project/Framework). 
PDS is composed of two modules: the Privacy module and the Data Sovereignty module.
Each module can be used independently from the other.

The [Privacy module](doc/Privacy.md) enables the creation of *privacy preserving surveys*. These are surveys
that allow users to add *noise* to their responses, using local differential privacy mechanisms.
The addition of the noise prevents 3rd parties from learning meaningful information about specific users, but at
the same time aggregated statistics can be extracted. The accuracy of the extracted statistics depends on the
number of responses. 

The [Data Sovereignty module](doc/Data-Sovereignty.md) implements an OAuth 2.0 Authorization Server. This server
accepts *authorization grants8 and if the grant is valid it generates an *access token* encoded using the
JSON web token format. Accepted types of authorization grants are: Decentralized Identifiers, Verifiable Credentials, and pre-shared secret keys. The generated web token can be used by any web service, as well as with SOFIE's
[Identity, Authentication, and Authorization (IAA) Component](https://github.com/SOFIE-project/identity-authentication-authorization)  


## Usage
* For the Privacy module, see the [Privacy module documentation](doc/Privacy.md)
* For the Data Sovereignty module, see the [Data Sovereignty module documentation](doc/Data-Sovereignty.md)


## Contact info

Please use github issues page  in case of any questions.

***