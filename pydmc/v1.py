from typing import Dict, List, Union

import requests
from pydmc.exceptions import AuthException, IICSException


class IICSV1Client:
    LOGIN_BASE_URL = "https://dm1-us.informaticacloud.com"
    base_url = None
    session_id = None
    org_id = None
    org_name = None

    def __init__(self, username: str, password: str):
        """
        Initialize a new instance of the IICSV1Client

        :param username: username to login with
        :type username: str
        :param password: password to login with
        :type password: str
        :return: a new instance of IICSV1Client
        :rtype: IICSV1Client
        :raises: AuthException
        """
        self._http = requests.Session()
        self.username = username
        self.password = password

        if not self.username:
            raise AuthException("No username provided")
        if not self.password:
            raise AuthException("No password provided")

        # Login on init to ensure that org information gets set
        # And capture any auth issues
        self._login()

    def _login(self):
        """
        Make a request to the IICS v3 login API to generate a new session for the user
        """

        # prepare the url and body for the request
        url = f"{self.LOGIN_BASE_URL}/ma/api/v2/user/login"
        body = {"@type": "login", "username": self.username, "password": self.password}

        # Make the login request
        r = requests.post(url, json=body)

        # Check the status
        try:
            r.raise_for_status()
        except requests.RequestException as e:
            raise IICSException(e.request, e.response)

        json_response = r.json()
        self.base_url = (
            "https://usw3.dm1-us.informaticacloud.com"  # json_response.get("serverUrl")
        )
        self.session_id = json_response.get("icSessionId")
        self.orgId = json_response.get("orgUuid")
        self.orgName = json_response.get("orgId")

    def _init_session(self):
        """
        Perform login and return session id

        :return: IDS-SESSION-ID
        :rtype: str
        """
        self._login()
        return self.session_id

    def _request(
        self,
        method: str,
        endpoint: str,
        timeout: int = 30,
        params: Dict[str, str] = {},
        body: Union[List, Dict] = {},
    ):
        """
        Make an HTTP request to the IICS API

        :param method: Which request method to use ["POST", "PUT", "GET", "DELETE", "HEAD", "OPTIONS"]
        :type method: str
        :param endpoint: which endpoint path to make a request to e.g. /public/core/v3/login
        :type endpoint: str
        :param timeout: how long to wait before timing out request
        :type timeout: int
        :param params: Set of key value pairs to send as url parameters in the request e.g. ?key=value
        :type params: Dict[str,str]
        :param body: HTTP body to send with the request
        :type body: Union[List, Dict]

        :raises: IICSEXception
        """

        # Build all of the request args
        request_args = {}
        request_args["params"] = params if params else {}
        request_args["json"] = body
        request_args["timeout"] = timeout
        request_args["headers"] = {"IDS-SESSION-ID": self._init_session()}

        # Set the full url, this must come after the login,
        # as the base url will be set by the return value of the login
        if not endpoint.startswith("/"):
            url = f"{self.base_url}/{endpoint}"
        else:
            url = f"{self.base_url}{endpoint}"

        r = self._http.request(method=method, url=url, **request_args)
        try:
            r.raise_for_status()
        except requests.RequestException as e:
            raise IICSException(e.request, e.response)

        return r

    def get_documents(self, document_type: str) -> List[dict]:
        """
        Retrieve a list of all documents, must provide the document type to search for e.g. TASKFLOW

        :param document_type: The type of document to search for (e.g. TASKFLOW, MAPPING)
        :type document_type: str
        :return: list of documents
        :rtype: List
        """
        r = self._request(
            "GET", f"/frs/api/v1/Documents?filter=(documentType eq '{document_type}')"
        )
        return r.json()
