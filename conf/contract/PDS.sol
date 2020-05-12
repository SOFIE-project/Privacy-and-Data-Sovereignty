pragma solidity ^0.5.0;
import { Ownable } from "@openzeppelin/contracts/ownership/Ownable.sol";
contract PDS is Ownable {
    event token_added (uint index, bytes DID);
    struct token_entry {
        bytes metadata;
        bytes DID;
        bytes enc_token;
    }
    token_entry[] tokens;
    function new_token(bytes memory metadata, bytes memory DID, bytes memory enc_token) public onlyOwner {
        tokens.push(token_entry(metadata, DID, enc_token));
        emit token_added(tokens.length-1, DID);
    }
}