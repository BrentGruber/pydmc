from typing import Dict, List, Union

import requests

from pydmc.exceptions import AuthException, IICSException


class IICSV2Client:
    LOGIN_BASE_URL = "https://dm1-us.informaticacloud.com"
    base_url = None
    session_id = None
    orgId = None
    orgName = None

    def __init__(self, username: str, password: str, auto_retry: bool = False):
        """
        Initialize a new instance of the IICSV2Client

        :param username: username to login with
        :type username: str
        :param password: password to login with
        :type password: str
        :return: a new instance of IICSV2Client
        :rtype: IICSV2Client
        :raises: AuthException
        """
        self._http = requests.Session()
        self.username = username
        self.password = password
        self.auto_retry = auto_retry

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
            raise IICSException(e)

        json_response = r.json()
        self.base_url = json_response.get("serverUrl")
        self.session_id = json_response.get("icSessionId")
        self.orgId = json_response.get("orgUuid")
        self.orgName = json_response.get("orgId")

    def _init_session(self):
        """
        Perform login and return session id

        :return: icSessionID
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
        request_args["headers"] = {"icSessionId": self._init_session()}

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
            raise IICSException(e)

        return r

    def get_org_details(self) -> Dict:
        """
        Get the details of the current organization, includes sub orgs

        :return: The organization details
        "rtype: Dict
        """
        r = self._request("GET", "/api/v2/org")
        return r.json()

    def get_org_by_id(self, org_id: str) -> Dict:
        """
        Get the details of an organization by id

        :param org_id: id of the org to retrieve details for
        :type org_id: str
        :return: the org object
        :rtype: Dict
        """
        r = self._request("GET", f"/api/v2/org/{org_id}")
        return r.json()

    def get_org_by_name(self, org_name: str) -> Dict:
        """
        Get the details of an organization by id

        :param org_name: name of the org to retrieve details for
        :type org_name: str
        :return: the org object
        :rtype: Dict
        """
        r = self._request("GET", f"/api/v2/org/name/{org_name}")
        return r.json()

    def get_runtime_environments(self) -> Dict:
        """
        Get the details of all runtime environments (Secure Agents)

        :return: the runtime environment object
        :rtype: Dict
        """
        r = self._request("GET", "/api/v2/runtimeEnvironment")
        return r.json()

    def get_runtime_environment_by_id(self, run_env_id: str) -> Dict:
        """
        Get the details of a runtime environment by id

        :param run_env_id: id of the runtime environment to retrieve details
        :type run_env_id: str
        :return: the runtime environment object
        :rtype: Dict
        """
        r = self._request("GET", f"/api/v2/runtimeEnvironment/{run_env_id}")
        return r.json()

    def get_runtime_environment_by_name(self, run_env_name: str) -> Dict:
        """
        Get the details of a runtime environment by name

        :param run_env_name: name of the runtime environment to retrieve details from
        :type run_env_name: str
        :return: the runtime environment object
        :rtype: Dict
        """
        r = self._request("GET", f"/api/v2/runtimeEnvironment/name/{run_env_name}")
        return r.json()

    def list_secure_agents(self) -> List[Dict]:
        """
        Get the list of secure agents

        :return: list of secure agents
        :rtype: Dict
        """
        r = self._request("GET", "/api/v2/agent")
        return r.json()

    def get_agent_by_id(self, agent_id: str) -> Dict:
        """
        Get a secure agent by id

        :param agent_id: id of the agent to get
        :type agent_id: str
        :return: Agent object
        :rtype: Dict
        """
        r = self._request("GET", f"/api/v2/agent/{agent_id}")
        return r.json()

    def get_agent_by_name(self, agent_name: str) -> Dict:
        """
        Get a secure agent by name

        :param agent_name: name of the agent to get
        :type agent_name: str
        :return: Agent object
        :rtype: Dict
        """
        r = self._request("GET", f"/api/v2/agent/name/{agent_name}")
        return r.json()

    def get_agent_details(self, agent_id: str, status: bool = False) -> Dict:
        """
        Get the secure agent details including service status

        :param agent_id: id of the agent to get
        :type agent_id: str
        :param status: if set to true, will return only the statuses of services without other details
        :type: bool
        :return: Agent Details object
        :rtype: Dict
        """
        params = {}
        if status:
            params["onlyStatus"] = "true"

        r = self._request("GET", f"/api/v2/agent/details/{agent_id}", params=params)
        return r.json()

    def get_server_time(self) -> Dict:
        """
        Return the local time for the Informatica Intelligent Cloud Services server

        TODO: Convert to datetime before returning

        :return: the local time of the server
        :rtype: Dict
        """
        r = self._request("GET", "/api/v2/server/serverTime")
        return r.json()

    def list_connections(self) -> List[Dict]:
        """
        List all of the connections

        :return: a list of all connections
        :rtype: List[Dict]
        """
        r = self._request("GET", "/api/v2/connection")
        return r.json()

    def get_connection(self, id) -> Dict:
        """
        Get a single connection by id

        :param id: id of the connection to retrieve
        :type id: str
        :return: a dictionary containing the connection details
        :rtype: Dict
        """
        r = self._request("GET", "/api/v2/connection/{id}")
        return r.json()

    def get_connection_by_name(self, connection) -> Dict:
        """
        Get a single connection by name

        :param connection: name of the connection to get details for
        :type connection: str
        :return: a dictionary containing the connection details
        :rtype: Dict
        """
        r = self._request("GET", "/api/v2/connection/name/{connection}")
        return r.json()

    def test_connection(self, id) -> Dict:
        """
        Test a connection

        :param id: id of the connection to test
        :type id: str
        :return: a dictionary indicating whether test was successful or not
        :rtype: Dict
        """
        r = self._request("GET", f"/api/v2/connection/test/{id}")
        return r.json()


#    def get_activity_log(self):
#        """
#        Get activity log
#        """
#        r = self._request("GET", "/api/v2/activity/activityLog?runId=")
