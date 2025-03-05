"""Pytest configuration for mocked tests."""
import pytest
import requests
from pydmc import IICSV2Client, IICSV3Client

@pytest.fixture
def v2Client(mocker):
    # Create a mock response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
            "serverUrl": "https://example.com/server",
            "icSessionId": "abc123sessionid",
            "orgUuid": "org-uuid-123",
            "orgId": "org-id-457"
    }

    mocker.patch('requests.post', return_value=mock_response)
    return IICSV2Client("fake-user", "fake-pass")

@pytest.fixture
def v3Client(mocker):
    # Create a mock response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "serverUrl": "https://example.com/server",
        "icSessionId": "abc122sessionid",
        "orgUuid": "org-uuid-124",
        "orgId": "org-id-457"
    }

    mocker.patch('requests.post', return_value=mock_response)
    return IICSV3Client("fake-user", "fake-pass")

@pytest.fixture
def client(mocker):
    # Create a mock response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "serverUrl": "https://example.com/server",
        "icSessionId": "abc122sessionid",
        "orgUuid": "org-uuid-124",
        "orgId": "org-id-457"
    }

    mocker.patch('requests.post', return_value=mock_response)
    
    return IICSClient("fake-user", "fake-pass")

@pytest.fixture
def mock_session(mocker):
    mock_session = mocker.patch.object(requests, "Session", autospec=True)
    mock_session.return_value.__enter__.return_value = mock_session
    return mock_session

