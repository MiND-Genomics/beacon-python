import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from beacon_api.app import init, main, create_db_pool
from unittest import mock
import asyncpg
import asynctest
import json
import jwt
# from test.support import EnvironmentVarGuard
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

PARAMS = {'assemblyId': 'GRCh38',
          'referenceName': '1',
          'start': 10000,
          'referenceBases': 'A',
          'alternateBases': 'T'}


def generate_token():
    """Mock ELIXIR AAI token."""
    private_key = rsa.generate_private_key(public_exponent=65537,
                                           key_size=2048, backend=default_backend())
    pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                    format=serialization.PrivateFormat.PKCS8,
                                    encryption_algorithm=serialization.NoEncryption())
    token = jwt.encode({'iss': 'https://login.elixir-czech.org/oidc/'},
                       pem, algorithm='RS256')

    public_key = private_key.public_key()
    pem_pub = public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                      format=serialization.PublicFormat.PKCS1)
    return token, pem_pub


async def create_db_mock(app):
    """Mock the db connection pool."""
    app['pool'] = asynctest.mock.Mock(asyncpg.create_pool())
    return app


async def mock_parse_request_object(request):
    """Mock parse request object."""
    return 'GET', json.dumps(PARAMS)


class AppTestCase(AioHTTPTestCase):
    """Test for Web app.

    Testing web app endpoints.
    """

    async def get_application(self):
        """Retrieve web Application for test."""
        with asynctest.mock.patch('beacon_api.app.create_db_pool', side_effect=create_db_mock):
            return init()

    @unittest_run_loop
    async def test_info(self):
        """Test the info endpoint.

        The status should always be 200.
        """
        with asynctest.mock.patch('beacon_api.app.beacon_info', side_effect={"smth": "value"}):
            resp = await self.client.request("GET", "/")
        assert 200 == resp.status

    @unittest_run_loop
    async def test_post_info(self):
        """Test the info endpoint with POST.

        The status should always be 405.
        """
        resp = await self.client.request("POST", "/")
        assert 405 == resp.status

    @unittest_run_loop
    async def test_empty_get_query(self):
        """Test empty GET query endpoint."""
        resp = await self.client.request("GET", "/query")
        assert 400 == resp.status

    @unittest_run_loop
    async def test_empty_post_query(self):
        """Test empty POST query endpoint."""
        resp = await self.client.request("POST", "/query", data=json.dumps({}))
        assert 400 == resp.status

    @unittest_run_loop
    async def test_unauthorized_no_token_post_query(self):
        """Test unauthorized POST query endpoint, with no token."""
        resp = await self.client.request("POST", "/query",
                                         data=json.dumps(PARAMS),
                                         headers={'Authorization': "Bearer"})
        assert 401 == resp.status

    @unittest_run_loop
    async def test_unauthorized_token_post_query(self):
        """Test unauthorized POST query endpoint, bad token."""
        resp = await self.client.request("POST", "/query",
                                         data=json.dumps(PARAMS),
                                         headers={'Authorization': "Bearer x"})
        assert 401 == resp.status

    @unittest_run_loop
    async def test_invalid_scheme_get_query(self):
        """Test unauthorized GET query endpoint, invalid scheme."""
        params = '?assemblyId=GRCh38&referenceName=1&start=10000&referenceBases=A&alternateBases=T'
        resp = await self.client.request("GET", f"/query{params}",
                                         headers={'Authorization': "SMTH x"})
        assert 401 == resp.status

    # @unittest_run_loop
    # async def test_valid_token_get_query(self):
    #     """Test unauthorized GET query endpoint, invalid scheme."""
    #     env = EnvironmentVarGuard()
    #     token = b'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2xvZ2luLmVsaXhpci1jemVjaC5vcmcvb2lkYy8ifQ.hVEk28a4BM7erZ3oSsaI5nAlwMRLOPxLMs-1vDp5bcXaJ4OQHLY_eH1ztqzWMkzMOI5uVgZi6lcgi4lz1_kEg8FEPDJkawgnIxdLmgYDTu8Kjm37bBwpR8TGinT7d-CuSzDmV5EgOqUVlRnxMv1Fhvnc1tCiwmKB-hJkEiah2inj7nrlvtgZa4soirghBfx5E6KTKxF6vFkREtO-5cvNXHxdfDEjes2gbhj7knjPQZkRfS9o_EZz1ne-RYmRfxS_1AunVFDWfY9bG2xgwaUWKB-92zowL4GGKZSVyYDoD8gLV-DqFM6-K3l2qVE3tR1zayGAJFNz2u1Eit_1JwjZAw'
    #     # print(token)
    #     public_key = "-----BEGIN PUBLIC KEY-----\nMIIBCgKCAQEApyOa+u5pQdZn4+JrA4aGrX+X/WnGr9el6OTx7crmvys3MjEo9UGr\n1ktbzOu8bYVEYp0jXqfUO8YzwvM/Mxn+7HBDXpCqpaBoS7MtD8XJ4DObRbeSSWsx\nB9d/MFoF36y5zzn8kHMerCMFMHobO/ZSTVC/1iO9RNeMyQWMnrn4Yod2zg2N6u1l\n0NlqWhDBpTwCw8yXPkP1CHRNOZ3SZYbbhophxfTgDnhBureT4Yq3s3b8Zan/M68s\nGu8pfmyFFcQpUSrw+nZO/Rw8FYqpMXOOZE1AbDqa5dhAUoAFtZSzrFG7OyKGV4mz\nv0B27O+J5DWFbeTEKZgJ9CQKE2zhXHuclwIDAQAB\n-----END PUBLIC KEY-----"
    #     env.set('PUBLIC_KEY', public_key)
    #     resp = await self.client.request("POST", "/query",
    #                                      data=json.dumps(PARAMS),
    #                                      headers={'Authorization': f"Bearer {token.decode('utf-8')}"})
    #     env.unset('PUBLIC_KEY')
    #     assert 200 == resp.status

    @unittest_run_loop
    async def test_bad_json_post_query(self):
        """Test bad json POST query endpoint."""
        resp = await self.client.request("POST", "/query", data="")
        assert 500 == resp.status

    @asynctest.mock.patch('beacon_api.app.parse_request_object', side_effect=mock_parse_request_object)
    @asynctest.mock.patch('beacon_api.app.query_request_handler', side_effect=json.dumps(PARAMS))
    @unittest_run_loop
    async def test_valid_get_query(self, mock_handler, mock_object):
        """Test valid GET query endpoint."""
        params = '?assemblyId=GRCh38&referenceName=1&start=10000&referenceBases=A&alternateBases=T'
        with asynctest.mock.patch('beacon_api.app.create_db_pool', side_effect=create_db_mock):
            resp = await self.client.request("GET", f"/query{params}")
        print(resp.text)
        print(dir(resp))
        assert 200 == resp.status

    @asynctest.mock.patch('beacon_api.app.parse_request_object', side_effect=mock_parse_request_object)
    @asynctest.mock.patch('beacon_api.app.query_request_handler', side_effect=json.dumps(PARAMS))
    @unittest_run_loop
    async def test_valid_post_query(self, mock_handler, mock_object):
        """Test valid POST query endpoint."""
        resp = await self.client.request("POST", "/query", data=json.dumps(PARAMS))
        assert 200 == resp.status


class TestBasicFunctionsApp(asynctest.TestCase):
    """Test App Base.

    Testing basic functions from web app.
    """

    def setUp(self):
        """Initialise fixtures."""
        pass

    def tearDown(self):
        """Remove setup variables."""
        pass

    @mock.patch('beacon_api.app.web')
    def test_main(self, mock_webapp):
        """Should start the webapp."""
        main()
        mock_webapp.run_app.assert_called()

    def test_init(self):
        """Test init type."""
        server = init()
        self.assertIs(type(server), web.Application)

    async def test_create_db_pool(self):
        """Test create db pool, should just return the result of init_db_pool.

        We will mock the init_db_pool, thus we assert we just call it.
        """
        app = {}
        with asynctest.mock.patch('beacon_api.app.init_db_pool') as db_mock:
            await create_db_pool(app)
            db_mock.assert_called()


if __name__ == '__main__':
    unittest.main()
