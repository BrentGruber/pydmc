"""Mock tests for the v2 API"""

import pytest
from requests.exceptions import HTTPError

from pydmc import IICSV2Client
from pydmc.exceptions import AuthException, IICSException

from .utils import mock_200_login_response, mock_200_response, mock_400_login_response


def test_init(v2Client):
    """
    Test the initialization of the class
    This also tests the login function indirectly
    """
    print(v2Client.username)
    assert v2Client.username == "fake-user"
    assert v2Client.password == "fake-pass"

    assert v2Client.base_url == "https://example.com/server"


def test_init_no_username():
    """
    Test initializing the client class without providing a username
    """
    try:
        client = IICSV2Client(None, "fake-pass")
    except AuthException as e:
        assert f"{e}" == "No username provided"
    else:
        # We should have caught an AuthException on the init
        # if we didn't then fail the test here
        assert False


def test_good_login(mocker, v2Client):
    """
    Test a successful login
    """
    mock_response = mock_200_login_response(mocker)
    mocker.patch("requests.post", return_value=mock_response)

    v2Client._login()
    assert v2Client.base_url == mock_response.json.return_value.get("serverUrl")
    assert v2Client.session_id == mock_response.json.return_value.get("icSessionId")
    assert v2Client.orgId == mock_response.json.return_value.get("orgUuid")
    assert v2Client.orgName == mock_response.json.return_value.get("orgId")


def test_bad_login(mocker, v2Client):
    """
    Test that a bad response on login will raise an IICSException
    """
    mock_response = mock_400_login_response(mocker)

    mocker.patch("requests.post", return_value=mock_response)

    try:
        v2Client._login()
    except IICSException as e:
        assert str(e) == "Simulated HTTP Error"
    else:
        assert False


def test_init_no_pass():
    """
    Test initializing the client class without providing a password
    """
    try:
        client = IICSV2Client("fake-user", None)
    except AuthException as e:
        assert f"{e}" == "No password provided"
    else:
        # We should have caught an AuthException on the init
        # if we didn't then fail the test here
        assert False


def test_post_request(mocker, v2Client):
    """
    Test that internal request function is returning the proper response body and status code
    when performing a post request
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "serverUrl": "https://example.com/server",
        "icSessionId": "abc122sessionid",
        "orgUuid": "org-uuid-124",
        "orgId": "org-id-457",
    }

    mocker.patch("requests.Session.request", return_value=mock_response)

    method = "POST"
    endpoint = "/my/awesome/api"
    body = {"foo": "fighters", "bar": "stools"}

    response = v2Client._request(method, endpoint, body=body)
    assert response.status_code == 200
    assert response.json() == mock_response.json.return_value


def test_get_request(mocker, v2Client):
    """
    Test that internal request function is returning the proper response body and status code
    when performing a get request
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "ABC",
        "id": "123",
    }

    mocker.patch("requests.Session.request", return_value=mock_response)

    method = "GET"
    endpoint = "/my/awesome/api"

    response = v2Client._request(method, endpoint)
    assert response.status_code == 200
    assert response.json() == mock_response.json.return_value


def test_bad_request(mocker, v2Client):
    """
    When the IICS api returns a 400-499 error code
    The client should raise an IICSException
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.text = "Error with request"

    mocker.patch("requests.Session.request", return_value=mock_response)

    method = "POST"
    endpoint = "this/is/a/bad/endpoint"
    body = {"seg": "fault"}

    try:
        response = v2Client._request(method, endpoint, body=body)
    except IICSException as e:
        print("RECEIVED EXCEPTION")
        assert False

    assert response.status_code == 400
    assert response.text == "Error with request"


def test_get_org_details(mocker, v2Client):
    """
    Test function for getting the org details
    _request has already been tested, we will just test any processing logic or serialization here
    """
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"testing": "that", "response": "is-serialized"}

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    org = v2Client.get_org_details()

    assert type(org) == dict
    assert org == {"testing": "that", "response": "is-serialized"}


def test_get_org_by_id(mocker, v2Client):
    """
    Test function for getting the org details by id
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    org = v2Client.get_org_by_id("my-org-id")

    assert type(org) == dict
    assert org == mock_response.json.return_value


def test_get_org_by_name(mocker, v2Client):
    """
    Test function for getting the org details by name
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    org = v2Client.get_org_by_name("my-org-name")

    assert type(org) == dict
    assert org == mock_response.json.return_value


def test_successful_get_runtime_environments(mocker, v2Client):
    """
    Test function for getting the runtime environments of the current organization
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    runtime_envs = v2Client.get_runtime_environments()

    assert type(runtime_envs) == dict
    assert runtime_envs == mock_response.json.return_value


def test_successful_get_runtime_environment_by_id(mocker, v2Client):
    """
    Test function for getting the runtime environment by id
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    runtime_env = v2Client.get_runtime_environment_by_id("my-runtime-id")

    assert type(runtime_env) == dict
    assert runtime_env == mock_response.json.return_value


def test_successful_get_runtime_environment_by_name(mocker, v2Client):
    """
    Test function for getting the runtime environment by name
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    runtime_env = v2Client.get_runtime_environment_by_name("my-runtime-name")

    assert type(runtime_env) == dict
    assert runtime_env == mock_response.json.return_value


def test_successful_list_secure_agents(mocker, v2Client):
    """
    Test function for listing the runtime envirnoments
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    secure_agents = v2Client.list_secure_agents()

    assert type(secure_agents) == dict
    assert secure_agents == mock_response.json.return_value


def test_successful_get_agent_by_id(mocker, v2Client):
    """
    Test function for getting an agent by id
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    secure_agent = v2Client.get_agent_by_id("my-agent-id")

    assert type(secure_agent) == dict
    assert secure_agent == mock_response.json.return_value


def test_successful_get_agent_by_name(mocker, v2Client):
    """
    Test function for getting an agent by name
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    secure_agent = v2Client.get_agent_by_name("my-agent-name")

    assert type(secure_agent) == dict
    assert secure_agent == mock_response.json.return_value


def test_get_agent_details(mocker, v2Client):
    """
    Test function for getting agent details
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    agent_details = v2Client.get_agent_details("my-agent-id")

    assert type(agent_details) == dict
    assert agent_details == mock_response.json.return_value


def test_get_server_time(mocker, v2Client):
    """
    Test function for getting server time
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    server_time = v2Client.get_server_time()

    assert type(server_time) == dict
    assert server_time == mock_response.json.return_value


def test_list_connections(mocker, v2Client):
    """
    Test function for listing connections
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    connections = v2Client.list_connections()

    assert type(connections) == dict
    assert connections == mock_response.json.return_value


def test_get_connection(mocker, v2Client):
    """
    Test function for getting a connection by ID
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    connection = v2Client.get_connection("my-connection-id")

    assert type(connection) == dict
    assert connection == mock_response.json.return_value


def test_get_connection_by_name(mocker, v2Client):
    """
    Test function for getting a connection by name
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    connection = v2Client.get_connection_by_name("my-connection-name")

    assert type(connection) == dict
    assert connection == mock_response.json.return_value


def test_test_connection(mocker, v2Client):
    """
    Test function for testing a connection
    """
    mock_response = mock_200_response(mocker)

    mocker.patch("pydmc.IICSV2Client._request", return_value=mock_response)

    test_result = v2Client.test_connection("my-connection-id")

    assert type(test_result) == dict
    assert test_result == mock_response.json.return_value
