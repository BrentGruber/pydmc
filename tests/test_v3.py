"""Mock tests for the v3 API"""

from pydmc import IICSV3Client
from pydmc.exceptions import AuthException, IICSException

from .utils import (
    mock_200_login_response,
    mock_200_response,
    mock_400_login_response,
    mock_400_response,
)


def test_init(v3Client):
    """
    Test the initialization of the class
    This also tests the login function indirectly
    """
    assert v3Client.username == "fake-user"
    assert v3Client.password == "fake-pass"
    assert v3Client.base_url == "https://example.com/server"


def test_init_no_username():
    """
    Test initializing the client class without providing a username
    Should raise an AuthException
    """
    try:
        client = IICSV3Client(None, "fake-pass")
    except AuthException as e:
        assert f"{e}" == "No username provided"
    else:
        # We should have caught an AuthException on the init
        # if we didn't then fail the test here
        assert False


def test_init_no_pass():
    """
    Test initializing the client class without providing a password
    """
    try:
        client = IICSV3Client("fake-user", None)
    except AuthException as e:
        assert f"{e}" == "No password provided"
    else:
        assert False


def test_good_login(mocker, v3Client):
    """
    Test a successful login
    """
    mock_response = mock_200_login_response(mocker)
    mocker.patch("requests.post", return_value=mock_response)

    v3Client._login()
    assert v3Client.base_url == mock_response.json.return_value.get("serverUrl")
    assert v3Client.session_id == mock_response.json.return_value.get("icSessionId")
    assert v3Client.orgId == mock_response.json.return_value.get("orgId")


def test_bad_login(mocker, v3Client):
    """
    Test that a bad response will raise an IICSException
    """
    mock_response = mock_400_login_response(mocker)

    mocker.patch("requests.post", return_value=mock_response)

    try:
        v3Client._login()
    except IICSException as e:
        assert str(e) == "Simulated HTTP Error"
    else:
        # If no exception was thrown then fail the test
        assert False


def test_post_request(mocker, v3Client):
    """
    Test that internal request function is returning the proper response body and status code
    when performing a post request
    """
    mock_response = mock_200_response(mocker)
    mocker.patch("requests.Session.request", return_value=mock_response)

    method = "POST"
    endpoint = "/my/awesome/api"
    body = {"foo": "fighters", "bar": "stools"}

    response = v3Client._request(method, endpoint, body=body)
    assert response.status_code == 200
    assert response.json() == mock_response.json.return_value


def test_get_request(mocker, v3Client):
    """
    Test that internal request function is returning the proper response body and status code
    when performing a get request
    """
    mock_response = mock_200_response(mocker)
    mocker.patch("requests.Session.request", return_value=mock_response)

    method = "GET"
    endpoint = "/my/awesome/api"

    response = v3Client._request(method, endpoint)
    assert response.status_code == 200
    assert response.json() == mock_response.json.return_value


def test_bad_request(mocker, v3Client):
    """
    When the IICS api returns a 400-499 error code
    The client should raise an IICSException
    """
    mock_response = mock_400_response(mocker)
    mocker.patch("requests.Session.request", return_value=mock_response)

    method = "POST"
    endpoint = "this/is/a/bad/endpoint"
    body = {"seg": "fault"}

    try:
        response = v3Client._request(method, endpoint, body=body)
    except IICSException as e:
        assert True
    else:
        assert False
