from typing import Dict, List

from pydmc.v1 import IICSV1Client
from pydmc.v2 import IICSV2Client
from pydmc.v3 import IICSV3Client


class IICSClient:
    def __init__(self, username: str, password: str) -> None:
        self.v1 = IICSV1Client(username, password)
        self.v2 = IICSV2Client(username, password)
        self.v3 = IICSV3Client(username, password)

    def get_org_details(self) -> Dict:
        """
        Get the details of the current organization, includes sub orgs

        :return: The organization details
        "rtype: Dict
        """
        org = self.v2.get_org_details()
        return org

    def get_org_by_id(self, org_id: str) -> Dict:
        """
        Get the details of an organization by id

        :param org_id: id of the org to retrieve details for
        :type org_id: str
        :return: the org object
        :rtype: Dict
        """
        org = self.v2.get_org_by_id(org_id)
        return org

    def get_org_by_name(self, org_name: str) -> Dict:
        """
        Get the details of an organization by id

        :param org_name: name of the org to retrieve details for
        :type org_name: str
        :return: the org object
        :rtype: Dict
        """
        org = self.v2.get_agent_by_name(org_name)
        return org

    def get_runtime_environments(self) -> Dict:
        """
        Get the details of all runtime environments (Secure Agents)

        :return: the runtime environment object
        :rtype: Dict
        """
        r = self.v2.get_runtime_environments()
        return r

    def get_runtime_environment_by_id(self, run_env_id: str) -> Dict:
        """
        Get the details of a runtime environment by id

        :param run_env_id: id of the runtime environment to retrieve details
        :type run_env_id: str
        :return: the runtime environment object
        :rtype: Dict
        """
        r = self.v2.get_runtime_environment_by_id(run_env_id)
        return r

    def get_runtime_environment_by_name(self, run_env_name: str) -> Dict:
        """
        Get the details of a runtime environment by name

        :param run_env_name: name of the runtime environment to retrieve details from
        :type run_env_name: str
        :return: the runtime environment object
        :rtype: Dict
        """
        r = self.v2.get_runtime_environment_by_name(run_env_name)
        return r

    def list_secure_agents(self) -> List[Dict]:
        """
        Get the list of secure agents

        :return: list of secure agents
        :rtype: Dict
        """
        r = self.v2.list_secure_agents()
        return r

    def get_agent_by_id(self, agent_id: str) -> Dict:
        """
        Get a secure agent by id

        :param agent_id: id of the agent to get
        :type agent_id: str
        :return: Agent object
        :rtype: Dict
        """
        r = self.v2.get_agent_by_id(agent_id)
        return r

    def get_agent_by_name(self, agent_name: str) -> Dict:
        """
        Get a secure agent by name

        :param agent_name: name of the agent to get
        :type agent_name: str
        :return: Agent object
        :rtype: Dict
        """
        r = self.v2.get_agent_by_name(agent_name)
        return r

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
        r = self.v2.get_agent_details(agent_id, status)
        return r

    def get_server_time(self) -> Dict:
        """
        Return the local time for the Informatica Intelligent Cloud Services server

        TODO: Convert to datetime before returning

        :return: the local time of the server
        :rtype: Dict
        """
        r = self.v2.get_server_time()
        return r

    def list_connections(self) -> List[Dict]:
        """
        List all of the connections

        :return: a list of all connections
        :rtype: List[Dict]
        """
        r = self.v2.list_connections()
        return r

    def retrieve_trusted_ips(self) -> Dict:
        """
        Retrieve the trusted IP ranges for the current organization

        :returns: Dictionary containing the trusted ip ranges
        :rtype: Dict
        """
        r = self.v3.retrieve_trusted_ips()
        return r

    def list_privileges(self) -> List[dict]:
        """
        List all of the privileges in the current Organization

        TODO: add filtering
        """
        r = self.v3.list_privileges()
        return r

    def list_roles(self) -> List[dict]:
        """
        List all of the roles in the current Organization
        """
        r = self.v3.list_roles()
        return r

    def get_role_details(self, role_name: str) -> List[dict]:
        """
        Get the details for a specific role in the organization

        :param role_name - str: the name of the role for which to retrieve details
        """
        r = self.v3.get_role_details(role_name)
        return r

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
        r = self.v3.create_role(role_name, description, privileges)
        return r

    def add_role_privileges(self, role_id: str, privileges: List[str]) -> bool:
        """
        Add privileges to an existing role using the role id

        :param role_id - str: id of the role to update
        :param privileges - List[str] - list of privilege names to add, e.g. ["view.auditLog", "ai.data.viewer"]
        :return: True if successful, else False
        :rtype: bool
        """
        r = self.v3.add_role_privileges(role_id, privileges)
        return r

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
        r = self.v3.add_role_privileges_by_name(role_name, privileges)
        return r

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
        r = self.v3.remove_role_privileges(role_id, privileges)
        return r

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
        r = self.v3.remove_role_privileges_by_name(role_name, privileges)
        return r

    def delete_role(self, role_id: str) -> bool:
        """
        Delete an existing role

        :param role_id: id of the role to delete
        :type role_id: str
        :return: True if successful, else False
        :rtype: bool
        """
        r = self.v3.delete_role(role_id)
        return r

    def list_users(self, limit: int = 100, skip: int = 0) -> List[dict]:
        """
        List all existing users

        :param limit: Maximum number of users to return. Maximum of 200. Default is 100.
        :type limit: int
        :param skip: Amount to offset the list of results.
            e.g. if you have already received users 0-25
            set the skip to 25 to get 25-50
        :type skip: int
        :return: List of all the existing users in the organization
        :rtype: List[dict]
        """
        r = self.v3.list_users(limit, skip)
        return r

    def get_user_by_id(self, user_id: str) -> Dict:
        """
        Retrieve a single user by their user Id

        :param user_id: id of the user to search for
        :type user_id: str
        :returns: the User object if found
        :rtype: Dict
        :raises NotFoundError
        """
        r = self.v3.get_user_by_id(user_id)
        return r

    def get_user_by_name(self, user_name: str) -> Dict:
        """
        Retrieve a single user by their name

        :param user_name: name of the user to search for
        :type user_name: str
        :returns: the user object if found
        :rtype: Dict
        :raises NotFoundError
        """
        r = self.v3.get_user_by_name(user_name)
        return r

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
        r = self.v3.list_user_groups(limit, skip)
        return r

    def get_user_group_by_id(self, group_id: str) -> Dict:
        """
        Search for a specific user group by id

        :param group_id: id of the group to search for
        :type group_id: str
        :return: The group object if found
        :rtype: Dict
        :raises: NotFoundError - if there is no match for group id
        """
        r = self.v3.get_user_group_by_id(group_id)
        return r

    def get_user_group_by_name(self, group_name: str) -> Dict:
        """
        Search for a specific user group by id

        :param group_name: name of the group to search for
        :type group_id: str
        :return: The group object if found
        :rtype: Dict
        :raises: NotFoundError - if there is no match for group name
        """
        r = self.v3.get_user_group_by_name(self, group_name)
        return r

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
        r = self.v3.list_saml_role_mappings(limit, skip)
        return r

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
        r = self.v3.list_saml_group_mappings(limit, skip)
        return r

    def add_saml_group_mappings(
        self, group_mappings: List[Dict], reuseGroup: bool = False
    ) -> bool:
        """
        Add a new saml group mapping to the organization

        :param group_mappings: a list of group mappings to add, each group mapping should follow the format
            {"roleName": "Admin", "samlGroupName": ["gg-aad-app-iics-superadmin-np"]}
        :type group_mappings: List[dict]
        :param reuseGroup: Whether or not to reuse the existing group
            if the group name is the same as the SAML group name
            if set to False, a new group will be created
        :type reuseGroup: bool
        :return: True if successful, else False
        :rtype: bool
        """
        r = self.v3.add_saml_group_mappings(group_mappings, reuseGroup)
        return r

    def remove_saml_group_mappings(self, group_mappings: List[Dict]) -> bool:
        """
        Remove existing saml group mappings from organization

        :param group_mappings: a list of group mappings to remove, each group mapping should follow the format
            {"roleName": "Admin", "samlGroupName": ["gg-aad-app-iics-superadmin-np"]}
        :type group_mappings: List[dict]
        :return: True if successful, else False
        :rtype: bool
        """
        r = self.v3.remove_saml_group_mappings(group_mappings)
        return r

    def list_schedules(self) -> List[dict]:
        """
        List all of the schedules in the current organization

        :return: A list of all the existing schedules
        :rtype: List[dict]
        """
        r = self.v3.list_schedules()
        return r

    def list_connections(self) -> List[dict]:
        """
        List all of the connections in the current organization

        :return: a list of all the existing connections
        :rtype: List[dict]
        """
        r = self.v2.list_connections()
        return r

    def get_connection_by_id(self, id: str) -> Dict:
        """
        Get a single connection by id

        :param id: id of the connection to retrieve
        :type id: str
        :return: a dictionary with the connection details
        :rtype: Dict
        """
        r = self.v2.get_connection(id=id)
        return r

    def get_connection_by_name(self, connection: str) -> Dict:
        """
        Get a single connection by name

        :param name: name of the connection to retrieve
        :type name: str
        :return: a dictionary with the connection details
        :rtype: Dict
        """
        r = self.v2.get_connection_by_name(connection=connection)
        return r

    def test_connection(self, id: str) -> Dict:
        """
        Test a connection and return a dictionary indicating whether it was successful

        :param id: id of the connection to test
        :type id: str
        :return: a dictionary indicating result of the test
        :rtype: Dict
        """
        r = self.v2.test_connection(id=id)
        return r
