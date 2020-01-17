<?php


    if(isset($_POST['grant_type']) && $_POST['grant_type'] == 'verifiable_credentials')
    { 
        ini_set('display_errors',1);error_reporting(E_ALL);
        require_once('oauth2-server-php/src/OAuth2/Autoloader.php');
        OAuth2\Autoloader::register();
        // your public key strings can be passed in however you like
        $publicKey  = file_get_contents('./keys/pubkey.pem');
        $privateKey = file_get_contents('./keys/privkey.pem');

        // create storage
        $storage = new OAuth2\Storage\Memory(array('keys' => array(
            'public_key'  => $publicKey,
            'private_key' => $privateKey,
        )));

        $server = new OAuth2\Server($storage, array(
            'use_jwt_access_tokens' => true,
        ));
        $server->addGrantType(new OAuth2\GrantType\VerifiableCredentials($storage, array('issuer_did'=>'NKGKtcNwssToP5f7uhsEs4')));
        $server->handleTokenRequest(OAuth2\Request::createFromGlobals())->send();
    }
    
    
?>