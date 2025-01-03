"""Jira-specific tools for the agent."""
from typing import Any, Dict, Optional, Tuple

from langchain_community.utilities.jira import JiraAPIWrapper
from logger import logger
from pydantic import Field

from ..config.settings import settings
from .base import AgentTool


class JiraTicketTool(AgentTool):
    """Tool for interacting with Jira tickets."""

    jira: JiraAPIWrapper = Field(default_factory=JiraAPIWrapper, exclude=True)

    def __init__(self) -> None:
        """Initialize the Jira ticket tool."""
        super().__init__(
            name="jira_ticket",
            description="Tool for managing Jira tickets",
            verbose=settings.agent.verbose,
        )

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the tool synchronously.

        This is required by LangChain's BaseTool, but we'll use the async version.
        This implementation raises NotImplementedError to ensure async usage.
        """
        raise NotImplementedError("This tool only supports async execution")

    async def get_all_tickets(self) -> Dict[str, str]:
        """Get all tickets from Jira.

        Returns:
            A dictionary mapping ticket keys to their descriptions
        """
        try:
            logger.debug("Fetching all tickets from Jira")
            issues = self.jira.get_issues()
            result = {
                issue.key: f"{issue.fields.summary}\n{issue.fields.description}"
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
            issue = self.jira.get_issue(ticket_number)
            result = (issue.key, f"{issue.fields.summary}\n{issue.fields.description}")
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
            logger.debug(f"Searching tickets with JQL: {jql}")
            issues = self.jira.get_issues(jql)
            result = {
                issue.key: f"{issue.fields.summary}\n{issue.fields.description}"
                for issue in issues
            }
            logger.debug(f"Found {len(result)} tickets")
            return result
        except Exception as e:
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
        else:
            raise ValueError(f"Unknown operation: {operation}")
