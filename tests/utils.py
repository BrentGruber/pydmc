from requests.exceptions import HTTPError
import json
import requests

def mock_200_response(mocker):
    body = {"foo": "fighters", "bar": "none"}
    text = json.dumps(body)

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = body
    mock_response.text = text

    return mock_response

def mock_200_login_response(mocker):
    body = {
            "serverUrl": "https://example.com",
            "icSessionId": "abc123",
            "orgUuid": "uuid1234",
            "orgId": "id4"
    }
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = body

    return mock_response

def mock_400_response(mocker):
    body = {"status": "400", "message": "Bad Request"}
    text = json.dumps(body)

    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = body
    mock_response.text = text
    mock_response.raise_for_status.side_effect = requests.RequestException("Simulated HTTP Error")

    return mock_response

def mock_400_login_response(mocker):
    body = { "error": "User not authorized" }
    mock_response = mocker.Mock()
    mock_response.json.return_value = body
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = HTTPError("Simulated HTTP Error")

    return mock_response
