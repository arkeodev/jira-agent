"""Jira-specific tools for the agent."""
from typing import Any, Dict, Optional, Tuple

from atlassian import Jira
from logger import logger

from ..config.settings import settings
from .base import AgentTool


class JiraTicketTool(AgentTool):
    """Tool for interacting with Jira tickets."""

    jira: Jira = None
    _project_info: Dict[str, Any] | None = None  # Cache for project information

    def __init__(self) -> None:
        """Initialize the Jira ticket tool."""
        super().__init__(
            name="jira_ticket",
            description="Tool for managing Jira tickets",
            verbose=settings.agent.verbose,
        )
        self.jira = Jira(
            url=settings.jira_instance_url,
            username=settings.jira_username,
            password=settings.jira_api_token,
            cloud=True,
        )

    async def get_project_info(self, refresh: bool = False) -> Dict[str, Any]:
        """Get information about the configured project.

        Args:
            refresh: Whether to refresh the cached project info

        Returns:
            Dictionary containing project information
        """
        if self._project_info is None or refresh:
            try:
                logger.debug(f"Fetching project info for key: {settings.project_key}")
                projects = self.jira.projects()
                for project in projects:
                    if project["key"] == settings.project_key:
                        self._project_info = {
                            "key": project["key"],
                            "name": project["name"],
                            "id": project["id"],
                        }
                        logger.debug(f"Found project info: {self._project_info}")
                        break
                else:
                    available_projects = {p["key"]: p["name"] for p in projects}
                    logger.error(
                        f"Project {settings.project_key} not found. Available projects: {available_projects}"
                    )
                    self._project_info = {}
            except Exception as e:
                logger.error(f"Error getting project info: {e}", exc_info=True)
                self._project_info = {}

        return self._project_info

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the tool synchronously.

        This is required by LangChain's BaseTool, but we'll use the async version.
        This implementation raises NotImplementedError to ensure async usage.
        """
        raise NotImplementedError("This tool only supports async execution")

    async def get_projects(self) -> Dict[str, str]:
        """Get all available projects from Jira.

        Returns:
            A dictionary mapping project keys to their names
        """
        try:
            logger.debug("Fetching all projects from Jira")
            projects = self.jira.projects()
            result = {project["key"]: project["name"] for project in projects}
            logger.debug(f"Found {len(result)} projects: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting projects: {e}", exc_info=True)
            return {}

    async def get_all_tickets(self) -> Dict[str, str]:
        """Get all tickets from Jira.

        Returns:
            A dictionary mapping ticket keys to their descriptions
        """
        try:
            project_info = await self.get_project_info()
            if not project_info:
                return {}

            logger.debug(f"Fetching all tickets for project: {project_info['key']}")
            jql = f"project = {project_info['key']}"
            issues = self.jira.jql(jql)["issues"]
            result = {
                issue[
                    "key"
                ]: f"{issue['fields']['summary']}\n{issue['fields'].get('description', '')}"
                for issue in issues
            }
            logger.debug(f"Found {len(result)} tickets")
            return result
        except Exception as e:
            logger.error(f"Error getting tickets: {e}", exc_info=True)
            return {}

    async def get_ticket_data(
        self, ticket_number: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Get data for a specific ticket.

        Args:
            ticket_number: The Jira ticket number

        Returns:
            A tuple of (ticket key, ticket description) or (None, None) if not found
        """
        try:
            logger.debug(f"Fetching data for ticket: {ticket_number}")
            issue = self.jira.issue(ticket_number)
            result = (
                issue["key"],
                f"{issue['fields']['summary']}\n{issue['fields'].get('description', '')}",
            )
            logger.debug(f"Retrieved ticket data: {result[0]}")
            return result
        except Exception as e:
            logger.error(f"Error getting ticket data: {e}", exc_info=True)
            return None, None

    async def link_tickets(self, from_issue: str, to_issue: str) -> bool:
        """Link two Jira tickets.

        Args:
            from_issue: The source ticket key
            to_issue: The target ticket key

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Linking issues: {from_issue} -> {to_issue}")
            self.jira.create_issue_link("Relates", from_issue, to_issue)
            logger.info(f"Successfully linked issues: {from_issue} -> {to_issue}")
            return True
        except Exception as e:
            logger.error(f"Error linking issues: {e}", exc_info=True)
            return False

    async def add_comment(self, issue_key: str, comment: str) -> bool:
        """Add a comment to a Jira ticket.

        Args:
            issue_key: The ticket key
            comment: The comment text

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Adding comment to issue {issue_key}: {comment}")
            self.jira.add_comment(issue_key, comment)
            logger.info(f"Successfully added comment to issue {issue_key}")
            return True
        except Exception as e:
            logger.error(f"Error adding comment: {e}", exc_info=True)
            return False

    async def search_tickets(self, jql: str) -> Dict[str, str]:
        """Search for tickets using JQL.

        Args:
            jql: The JQL query string

        Returns:
            A dictionary mapping ticket keys to their descriptions
        """
        try:
            project_info = await self.get_project_info()
            if not project_info:
                return {}

            # Replace project name with key in JQL if needed
            if f"project = {project_info['name']}" in jql:
                jql = jql.replace(
                    f"project = {project_info['name']}",
                    f"project = {project_info['key']}",
                )
            elif "project =" not in jql:
                # Add project filter if not specified
                jql = f"project = {project_info['key']} AND {jql}"

            logger.debug(f"Searching tickets with JQL: {jql}")
            issues = self.jira.jql(jql)["issues"]
            result = {
                issue[
                    "key"
                ]: f"{issue['fields']['summary']}\n{issue['fields'].get('description', '')}"
                for issue in issues
            }
            logger.debug(f"Found {len(result)} tickets")
            return result
        except Exception as e:
            if "does not exist for the field 'project'" in str(e):
                # Log available projects when project not found
                projects = await self.get_projects()
                logger.error(f"Project not found. Available projects: {projects}")
            logger.error(f"Error searching tickets: {e}", exc_info=True)
            return {}

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Run the appropriate Jira operation based on the input.

        Args:
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            The result of the operation

        Raises:
            ValueError: If the operation is not recognized
        """
        # If a string is passed directly, treat it as a JQL query
        if len(args) == 1 and isinstance(args[0], str):
            return await self.search_tickets(args[0])

        operation = kwargs.get("operation")
        if not operation:
            raise ValueError("No operation specified")

        if operation == "get_all_tickets":
            return await self.get_all_tickets()
        elif operation == "get_ticket_data":
            ticket_number = kwargs.get("ticket_number")
            if not ticket_number:
                raise ValueError("No ticket number provided")
            return await self.get_ticket_data(ticket_number)
        elif operation == "link_tickets":
            from_issue = kwargs.get("from_issue")
            to_issue = kwargs.get("to_issue")
            if not from_issue or not to_issue:
                raise ValueError("Missing issue keys for linking")
            return await self.link_tickets(from_issue, to_issue)
        elif operation == "add_comment":
            issue_key = kwargs.get("issue_key")
            comment = kwargs.get("comment")
            if not issue_key or not comment:
                raise ValueError("Missing issue key or comment")
            return await self.add_comment(issue_key, comment)
        elif operation == "search_tickets":
            jql = kwargs.get("jql")
            if not jql:
                raise ValueError("No JQL query provided")
            return await self.search_tickets(jql)
        elif operation == "get_projects":
            return await self.get_projects()
        else:
            raise ValueError(f"Unknown operation: {operation}")
