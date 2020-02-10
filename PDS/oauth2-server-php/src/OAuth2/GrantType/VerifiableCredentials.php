<?php

namespace OAuth2\GrantType;

use OAuth2\RequestInterface;
use OAuth2\ResponseInterface;
use OAuth2\ResponseType\AccessTokenInterface;
use OAuth2\Storage\ClientCredentialsInterface;
use OAuth2\ClientAssertionType\ClientAssertionTypeInterface;

/**
 * @author Brent Shaffer <bshafs at gmail dot com>
 *
 * @see HttpBasic
 */
class VerifiableCredentials implements GrantTypeInterface, ClientAssertionTypeInterface
{
    /**
     * @var array
     */
    private $clientId;
    private $scope;
    private $userId;
    private $issuer_did;

    /**
     * @param ClientCredentialsInterface $storage
     * @param array $config
     */
    public function __construct(ClientCredentialsInterface $storage, array $config = array())
    {
        /**
         * The client credentials grant type MUST only be used by confidential clients
         *
         * @see http://tools.ietf.org/html/rfc6749#section-4.4
         */
        $config['allow_public_clients'] = false;

        $this->storage = $storage;
        $this->config = $config;
        $this->issuer_did = $config['issuer_did'];
        /*
        array_merge(array(
            'allow_credentials_in_request_body' => true,
            'allow_public_clients' => true,
        ), $config);
        */
    }

    /**
     * Get query string identifier
     *
     * @return string
     */
    public function getQueryStringIdentifier()
    {
        return 'verifiable_credentials';
    }

    /**
     * @param RequestInterface $request
     * @param ResponseInterface $response
     * @return mixed
     */
    public function validateRequest(RequestInterface $request, ResponseInterface $response)
    {
        $cred_def_id = $request->request('cred_def_id');
        $proof       = $request->request('proof');
        $this->scope       = $request->request('scope');
        $this->clientId    = $request->request('aud');
        $this->userId      = $request->request('sub');
        if($proof)
        {
            $proof_request = $this->generate_proof_request();
            exec("python3 ../Agent/PDS-agent.py -v -r '$proof_request' -p '$proof'",$output,$return_var);
            if($output[0] == 200)
                return true;
            else
                return false;
        }else
        {
            echo $this->generate_proof_request();
            return false;
        }
    }

    /**
     * Get scope
     *
     * @return string|null
     */
    public function getScope()
    {
        return $this->scope;
    }

    /**
     * Get client id
     *
     * @return mixed
     */
    public function getClientId()
    {
        return $this->clientId;
    }

    /**
     * Get user id
     *
     * @return mixed
     */
    public function getUserId()
    {
        return $this->userId;
    }

    /**
     * Create access token
     *
     * @param AccessTokenInterface $accessToken
     * @param mixed                $client_id   - client identifier related to the access token.
     * @param mixed                $user_id     - user id associated with the access token
     * @param string               $scope       - scopes to be stored in space-separated string.
     * @return array
     */
    public function createAccessToken(AccessTokenInterface $accessToken, $client_id, $user_id, $scope)
    {
        /**
         * Client Credentials Grant does NOT include a refresh token
         *
         * @see http://tools.ietf.org/html/rfc6749#section-4.4.3
         */
        $includeRefreshToken = false;

        return $accessToken->createAccessToken($client_id, $user_id, $scope, $includeRefreshToken);
    }

    private function generate_proof_request()
    {
        $issuer = $this->issuer_did;
        $nonce =  $this->get_nonce();
        $proof =  '{"nonce": "'.$nonce.'","name": "proof_req_1", "version": "0.1", "requested_attributes":';
        $proof .= '{"attr1_referent": {"name": "resources", "restrictions": [{"issuer_did": "'.$issuer.'"}]}}';
        $proof .= ',"requested_predicates": {}';
        $proof .= '}';
        return $proof;
    }

    private function get_nonce()
    {
        $nonce = rand(1,9);
        for($i=0; $i<30; $i++) {
            $nonce .= rand(0,9);
        }
        /*!!!!!!!!!!!DANGER FIX THIS!!!!!!!!!!!!*/
        $nonce = '9843787448916803398229937674313';
        return $nonce;
    }

}
