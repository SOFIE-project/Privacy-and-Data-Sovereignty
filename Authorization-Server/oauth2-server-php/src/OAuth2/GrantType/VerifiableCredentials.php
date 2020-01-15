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
    private $clientData;

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
        if($proof)
        {
            return true;
        }else
        {
            exec("python3 ../Agent/PDS-agent.py -o $cred_def_id",$output, $return_var);
            //$response->setParameter("cred_offer", $output[0]);
            echo $output[0];
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
        return null;
    }

    /**
     * Get client id
     *
     * @return mixed
     */
    public function getClientId()
    {
        return "clientId";
    }

    /**
     * Get user id
     *
     * @return mixed
     */
    public function getUserId()
    {
        return "userId";
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

}
