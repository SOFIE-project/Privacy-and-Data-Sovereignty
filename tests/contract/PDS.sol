pragma solidity ^0.4.0;

contract PDS
{
    
    struct token_entry{
        bytes DID;
        bytes enc_token;
    }
    
    token_entry[] tokens;
    
    event token_added (uint index, bytes DID);
    
    function new_token (bytes DID, bytes enc_token) public 
    {
        tokens.push(token_entry(DID, enc_token));
        emit token_added(tokens.length-1, DID);
    }
    
    function get_token(uint index) public view returns (bytes DID, bytes enc_token)
    {
        return(tokens[index].DID, tokens[index].enc_token);
    }
}