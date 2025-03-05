import logging
from typing import Any, Dict, List, Union

import requests
from pydmc.exceptions import AuthException, IICSException, NotFoundError

logger = logging.getLogger(__name__)


class IICSV3Client:
    LOGIN_BASE_URL = "https://dm1-us.informaticacloud.com/saas"
    base_url = None
    session_id = None
    orgId = None

    def __init__(self, username: str, password: str, auto_retry: bool = False):
        """
        Initialize the IICSClient instance

        :param username: the username used for connecting to IICS
        :type username: str
        :param password: the password used for connecting to IICS
        :type password: str
        :param auto_retry: whether to automatically retry any failed calls
        :type auto_retry: bool
        :return: A new instance of the IICSClient class
        :rtype: IICSClient
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
        url = f"{self.LOGIN_BASE_URL}/public/core/v3/login"
        body = {"username": self.username, "password": self.password}

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
        self.orgId = json_response.get("orgId")

    def _init_session(self):
        """
        Initiate a login session with IICS API and return the generated session ID

        :return: A session id that can be used for making subsequent api calls
        :rtype: str

        TODO: if there is a way to check whether the session is active locally,
        this would not need to make an extra api call to generate a new session.
        """
        self._login()

        return self.session_id

    def _request(
        self,
        method: str,
        endpoint: str,
        timeout: int = 30,
        params: Dict[str, Any] = {},
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
        request_args["headers"] = {"INFA-SESSION-ID": self._init_session()}

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

    def retrieve_trusted_ips(self) -> Dict:
        """
        Retrieve the trusted IP ranges for the current organization

        :returns: Dictionary containing the trusted ip ranges
        :rtype: Dict
        """
        r = self._request("GET", f"/public/core/v3/Orgs/{self.orgId}/TrustedIP")
        return r.json()

    def list_privileges(self) -> List[dict]:
        """
        List all of the privileges in the current Organization

        TODO: add filtering
        """
        r = self._request("GET", "/public/core/v3/privileges")
        return r.json()

    def list_roles(self) -> List[dict]:
        """
        List all of the roles in the current Organization
        """
        r = self._request("GET", "/public/core/v3/roles")
        return r.json()

    def get_role_details(self, role_name: str) -> List[dict]:
        """
        Get the details for a specific role in the organization

        :param role_name - str: the name of the role for which to retrieve details
        """
        params = {"q": f'roleName=="{role_name}"', "expand": "privileges"}
        r = self._request("GET", "/public/core/v3/roles", params=params)
        return r.json()

    def create_role(
        self, role_name: str, description: str = "", privileges: List[str] = []
    ) -> Dict:
        """
        Create a role in the current organization

        :param role_name: the name of the role to create
        :type role_name: str
        :param description: a short description of what the role is used for
        :type description: str
        :privileges: a list of the privilege ids to attach to this role,
        e.g. ["aQwUdcM8RcQewA1yWphZ4F", "0nTOXl8dzEwlSFoM0cO8gI"]
        :type privileges: List[str]
        :return: The newly created role
        :rtype: Dict
        """
        body = {"name": role_name, "description": description, "privileges": privileges}
        r = self._request("POST", "/public/core/v3/roles", body=body)
        return r.json()

    def add_role_privileges(self, role_id: str, privileges: List[str]) -> bool:
        """
        Add privileges to an existing role using the role id

        :param role_id - str: id of the role to update
        :param privileges - List[str] - list of privilege names to add, e.g. ["view.auditLog", "ai.data.viewer"]
        :return: True if successful, else False
        :rtype: bool
        """
        body = {"privileges": privileges}
        r = self._request(
            "PUT", f"/public/core/v3/roles/{role_id}/addPrivileges", body=body
        )
        return r.status_code == 204

    def add_role_privileges_by_name(
        self, role_name: str, privileges: List[str]
    ) -> bool:
        """
        Add privileges to an existing role using the role name

        :param role_name: the name of the role to update
        :type role_name: str
        :param privileges: list of privilege names to add to the role, e.g. ["view.auditLog", "ai.data.viewer"]
        :type privileges: List[str]
        :return: True if successful, else False
        :rtype: bool
        """
        body = {"privileges": privileges}
        r = self._request(
            "PUT", f"/public/core/v3/roles/name/{role_name}/addPrivileges", body=body
        )
        return r.status_code == 204

    def remove_role_privileges(self, role_id: str, privileges: List[str]) -> bool:
        """
        Remove privileges from an existing role by role id

        :param role_id: id of the role to remove privileges from
        :type role_id: str
        :param privileges: list of privilege names to remove from the role e.g. ["view.auditLog", "ai.data.viewer"]
        :type privileges: List[str]
        :return: True if successful, else False
        :rtype: bool
        """
        body = {"privileges": privileges}
        r = self._request(
            "PUT", f"/public/core/v3/roles/{role_id}/removePrivileges", body=body
        )
        return r.status_code == 204

    def remove_role_privileges_by_name(
        self, role_name: str, privileges: List[str]
    ) -> bool:
        """
        Remove privileges from an existing role by role name

        :param role_name: id of the role to remove privileges from
        :type role_id: str
        :param privileges: list of privilege names to remove from the role, e.g. ["view.auditLog", "ai.data.viewer"]
        :type privileges: List[str]
        :return: True if successful, else False
        :rtype: bool
        """
        body = {"privileges": privileges}
        r = self._request(
            "PUT", f"/public/core/v3/roles/name/{role_name}/removePrivileges", body=body
        )
        return r.status_code == 204

    def delete_role(self, role_id: str) -> bool:
        """
        Delete an existing role

        :param role_id: id of the role to delete
        :type role_id: str
        :return: True if successful, else False
        :rtype: bool
        """
        r = self._request("DELETE", f"/public/core/v3/roles/{role_id}")
        return r.status_code == 204

    def list_users(self, limit: int = 100, skip: int = 0) -> List[dict]:
        """
        List all existing users

        :param limit: Maximum number of users to return. Maximum of 200. Default is 100.
        :type limit: int
        :param skip: Amount to offset the list of results.
        e.g. if you have already received users 0-25 set the skip to 25
        to get 25-50
        :type skip: int
        :return: List of all the existing users in the organization
        :rtype: List[dict]
        """
        params = {"limit": limit, "skip": skip}
        r = self._request("GET", "/public/core/v3/users", params=params)
        return r.json()

    def get_user_by_id(self, user_id: str) -> Dict:
        """
        Retrieve a single user by their user Id

        :param user_id: id of the user to search for
        :type user_id: str
        :returns: the User object if found
        :rtype: Dict
        :raises NotFoundError
        """
        params = {"q": f"userId=={user_id}", "limit": 1, "skip": 0}
        r = self._request("GET", "/public/core/v3/users", params=params)
        matches = r.json()
        if matches == []:
            raise NotFoundError(
                f"User with id {user_id}, not found in current organization {self.orgName}"
            )
        return matches[0]

    def get_user_by_name(self, user_name: str) -> Dict:
        """
        Retrieve a single user by their name

        :param user_name: name of the user to search for
        :type user_name: str
        :returns: the user object if found
        :rtype: Dict
        :raises NotFoundError
        """
        params = {"q": f"userName=={user_name}", "limit": 1, "skip": 0}
        r = self._request("GET", "/public/core/v3/users", params=params)
        matches = r.json()
        if matches == []:
            raise NotFoundError(
                f"User with name {user_name} not found in current organization {self.orgName}"
            )
        return matches[0]

    def list_user_groups(self, limit: int = 100, skip: int = 0) -> List[dict]:
        """
        List all user groups in the organization

        :param limit: Maximum number of user groups to return, Default is 100
        :type limit: int
        :param skip: Amount to offset the list of results, Default is 0
        :type skip: int
        :return: list of user groups
        :rtype: List[dict]
        """
        params = {"limit": limit, "skip": skip}
        r = self._request("GET", "/public/core/v3/userGroups", params=params)
        return r.json()

    def get_user_group_by_id(self, group_id: str) -> Dict:
        """
        Search for a specific user group by id

        :param group_id: id of the group to search for
        :type group_id: str
        :return: The group object if found
        :rtype: Dict
        :raises: NotFoundError - if there is no match for group id
        """
        params = {"q": f"userGroupId=={group_id}", "limit": 1, "skip": 0}
        r = self._request("GET", "/public/core/v3/userGroups", params=params)
        matches = r.json()
        if matches == []:
            raise NotFoundError(
                f"User Group with id {group_id} was not found in current organization, {self.orgName}"
            )
        return matches

    def get_user_group_by_name(self, group_name: str) -> Dict:
        """
        Search for a specific user group by id

        :param group_name: name of the group to search for
        :type group_id: str
        :return: The group object if found
        :rtype: Dict
        :raises: NotFoundError - if there is no match for group name
        """
        params = {"q": f"userGroupName=={group_name}", "limit": 1, "skip": 0}
        r = self._request("GET", "/public/core/v3/userGroups", params=params)
        matches = r.json()
        if matches == []:
            raise NotFoundError(
                f"User Group with id {group_name} was not found in current organization, {self.orgName}"
            )
        return matches

    def list_saml_role_mappings(self, limit: int = 200, skip: int = 0) -> List[dict]:
        """
        List all of the existing saml role mappings in the organization

        :param limit: Maximum number of role mappings to return, Default is 200
        :type limit: int
        :param skip: Amount to offset the list of results, Default is 0
        :type skip: int
        :return: list of role mappings
        :rtype: List[dict]
        """
        params = {"limit": limit, "skip": skip}
        r = self._request(
            "GET",
            f"/public/core/v3/Orgs/{self.orgId}/SAMLConfig/roleMappings",
            params=params,
        )
        return r.json()

    def list_saml_group_mappings(self, limit: int = 200, skip: int = 0) -> List[dict]:
        """
        List all of the existing saml group mappings in the organization

        :param limit: Maximum number of group mappings to return, Default is 200
        :type limit: int
        :param skip: Amount to offset the list of results, Default is 0
        :type skip: int
        :return: list of role mappings
        :rtype: List[dict]
        """
        params = {"limit": limit, "skip": skip}
        r = self._request(
            "GET",
            f"/public/core/v3/Orgs/{self.orgId}/SAMLConfig/groupMappings",
            params=params,
        )
        return r.json()

    def add_saml_group_mappings(
        self, group_mappings: List[Dict], reuseGroup: bool
    ) -> bool:
        """
        Add a new saml group mapping to the organization

        :param group_mappings: a list of group mappings to add,
            each group mapping should follow the format
               {
                "roleName": "Admin",
                "samlGroupName": ["gg-aad-app-iics-superadmin-np"]
               }
        :type group_mappings: List[dict]
        :param reuseGroup: Whether or not to reuse the existing group if the
            group name is the same as the SAML group name
            if set to False, a new group will be created
        :type reuseGroup: bool
        :return: True if successful, else False
        :rtype: bool
        """
        body = {"groupMappings": group_mappings, "reuseGroup": reuseGroup}
        r = self._request(
            "PUT", f"/public/core/v3/Orgs/{self.orgId}/addSamlGroupMappings", body=body
        )
        return r.status_code == 204

    def remove_saml_group_mappings(self, group_mappings: List[Dict]) -> bool:
        """
        Remove existing saml group mappings from organization

        :param group_mappings: a list of group mappings to remove, each group mapping should follow the format
            {"roleName": "Admin", "samlGroupName": ["gg-aad-app-iics-superadmin-np"]}
        :type group_mappings: List[dict]
        :return: True if successful, else False
        :rtype: bool
        """
        body = {"groupMappings": group_mappings}
        r = self._request(
            "PUT",
            f"/public/core/v3/Orgs/{self.orgId}/removeSamlGroupMappings",
            body=body,
        )
        return r.status_code == 204

    def list_schedules(self) -> List[dict]:
        """
        List all of the schedules in the current organization

        :return: A list of all the existing schedules
        :rtype: List[dict]
        """
        r = self._request("GET", "/public/core/v3/schedule")
        return r.json()
