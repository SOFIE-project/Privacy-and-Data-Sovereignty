pragma solidity ^0.4.24;
/* Version 1.1 */

contract Access {

    struct policyRecord
    {
        address acp;
        string  URIpolicy;
        uint    price;
    }
    
    struct payment
    {
        address acp;
        uint    price;
        string  base64Hash;
    }
    
    mapping(string => policyRecord) private acl;
    mapping(string => payment) private pendingPayments;
    
    event authRequestSEvent(
        string token,
        string URIresource,
        string URIpolicy,
        string publicKey
    );

    event authRequest1Event(
        string token,
        string URIresource,
        string URIpolicy,
        string base64Hash,
        string publicKey
    );

    event authRequest2Event(
        string token,
        string URIresource,
        string URIpolicy,
        string base64Challenge,
        string publicKey
    );
    
    event authGrantedEvent(
         string publicKey,
         string token,
         string URIresource,
         string base64Esk
    );
    
    /* Create access control policy */
    function createACPolicy (string URIresource, string URIpolicy,  uint price ) external {
        policyRecord storage record = acl[URIresource];
        record.acp       = msg.sender;
        record.price     = price;
        record.URIpolicy = URIpolicy;
    }
    
    function getACPolicy (string URIresource) external view returns (address) {
        return acl[URIresource].acp;

    }
    
    /* Authorization Request no further check*/
    function authRequestS(string token, string URIresource, string publicKey ) external payable {
        require(msg.value >= acl[URIresource].price);
        payment storage record = pendingPayments[token];
        policyRecord memory policy = acl[URIresource];
        record.acp       = policy.acp;
        record.price     = msg.value;
        emit authRequestSEvent(token, URIresource, acl[URIresource].URIpolicy, publicKey);
    }
    
    /* Authorization Request, include the hash generated from the Thing*/
    function authRequest1(string token, string URIresource, string base64Hash, string publicKey  ) external payable {
        require(msg.value >= acl[URIresource].price);
        payment storage record = pendingPayments[token];
        policyRecord memory policy = acl[URIresource];
        record.acp   = policy.acp;
        record.price = policy.price;
        emit authRequest1Event(token, URIresource, acl[URIresource].URIpolicy, base64Hash, publicKey);
    }
    
    /* Authorization Request, include the hash generated from the Thing*/
    function authRequest2(string token, string URIresource, string base64challenge, string base64Hash, string publicKey ) external payable {
        require(msg.value >= acl[URIresource].price);
        payment storage record = pendingPayments[token];
        policyRecord storage policy = acl[URIresource];
        record.acp   = policy.acp;
        record.price = policy.price;
        record.base64Hash = base64Hash;
        emit authRequest2Event(token, URIresource, acl[URIresource].URIpolicy,base64challenge, publicKey);
    }
    
     /* Authorization granted */
    function authorize1(string publicKey, string token, string URIresource, string base64Esk) external {
        payment storage record = pendingPayments[token];
        //require (msg.sender == record.acp);
        msg.sender.transfer(record.price);
        delete pendingPayments[token];
        emit authGrantedEvent(publicKey, token, URIresource, base64Esk);
    }
    
    /* Authorization granted the Thing-publisher relationship verification*/
    function authorize2(string publicKey, string token, string URIresource, string base64Esk, string base64hashPreimage) external {
        payment storage record = pendingPayments[token];
        require (msg.sender == record.acp);
        bytes32 h = keccak256(abi.encodePacked(base64hashPreimage));
        msg.sender.transfer(record.price);
        delete pendingPayments[token];
        emit authGrantedEvent(publicKey, token, URIresource, base64Esk);
    }
    
    /* Authorization granted the Thing-publisher relationship verification*/
    function verifySignature(string message, bytes32 signature)  external view{
        require (keccak256(abi.encodePacked(message)) == signature);
    }
    
    
    
}
