"""Tool for triaging Jira tickets."""
import re
from typing import Any, Dict, Optional

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from logger import logger
from pydantic import Field

from ..config.prompts import create_ticket_analysis_prompt, create_ticket_linking_prompt
from ..llm.models import get_llm
from .base import AgentTool
from .jira import JiraTicketTool


class TicketTriageTool(AgentTool):
    """Tool for triaging Jira tickets."""

    jira_tool: JiraTicketTool = Field(default_factory=JiraTicketTool, exclude=True)
    llm: ChatOpenAI = Field(default_factory=get_llm, exclude=True)
    linking_prompt: ChatPromptTemplate = Field(
        default_factory=create_ticket_linking_prompt, exclude=True
    )
    analysis_prompt: ChatPromptTemplate = Field(
        default_factory=create_ticket_analysis_prompt, exclude=True
    )

    def __init__(self) -> None:
        """Initialize the ticket triage tool."""
        super().__init__(
            name="triage_ticket",
            description="Analyze and triage a Jira ticket, linking related tickets and adding relevant metadata",
        )

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the tool synchronously.

        This is required by LangChain's BaseTool, but we'll use the async version.
        This implementation raises NotImplementedError to ensure async usage.
        """
        raise NotImplementedError("This tool only supports async execution")

    async def check_ticket_match(self, ticket1: str, ticket2: str) -> bool:
        """Check if two tickets are related.

        Args:
            ticket1: First ticket description
            ticket2: Second ticket description

        Returns:
            True if tickets are related, False otherwise
        """
        try:
            logger.debug("Checking ticket match")
            llm_result = await self.llm.ainvoke(
                self.linking_prompt.format_prompt(
                    input=f"<ticket1>{ticket1}</ticket1><ticket2>{ticket2}</ticket2>"
                )
            )
            result = self._extract_tag(str(llm_result), "result")
            return result == "True" if result else False
        except Exception as e:
            logger.error(f"Error checking ticket match: {e}", exc_info=True)
            return False

    async def analyze_ticket(self, ticket_data: str) -> Optional[Dict[str, str]]:
        """Analyze a ticket to extract metadata.

        Args:
            ticket_data: The ticket description

        Returns:
            Dictionary containing extracted metadata or None if analysis fails
        """
        try:
            logger.debug("Analyzing ticket")
            llm_result = await self.llm.ainvoke(
                self.analysis_prompt.format_prompt(
                    input=f"<description>{ticket_data}</description>"
                )
            )
            result = str(llm_result)

            # Extract all fields and filter out None values
            extracted = {
                "user_stories": self._extract_tag(result, "user_stories"),
                "acceptance_criteria": self._extract_tag(result, "acceptance_criteria"),
                "priority": self._extract_tag(result, "priority"),
                "thought": self._extract_tag(result, "thought"),
            }

            # Only include fields that have values
            return {k: v for k, v in extracted.items() if v is not None} or None

        except Exception as e:
            logger.error(f"Error analyzing ticket: {e}", exc_info=True)
            return None

    def _extract_tag(self, text: str, tag: str) -> Optional[str]:
        """Extract content from XML-like tags.

        Args:
            text: The text to extract from
            tag: The tag name to extract

        Returns:
            The extracted content or None if not found
        """
        try:
            pattern = f"<{tag}>(.*?)</{tag}>"
            if match := re.search(pattern, text, re.DOTALL):
                return match.group(1).strip()
            return None
        except Exception as e:
            logger.error(f"Error extracting tag: {e}", exc_info=True)
            return None

    async def _arun(
        self,
        ticket_number: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run the triage tool on a ticket.

        Args:
            ticket_number: The ticket number to triage
            run_manager: Optional callback manager

        Returns:
            A message indicating the triage result
        """
        try:
            # Get ticket data
            all_tickets = await self.jira_tool.get_all_tickets()
            primary_key, primary_data = await self.jira_tool.get_ticket_data(
                ticket_number
            )

            if not primary_key or not primary_data:
                return f"Could not find ticket {ticket_number}"

            # Find and link related tickets
            for key, data in all_tickets.items():
                if key != primary_key and await self.check_ticket_match(
                    primary_data, data
                ):
                    await self.jira_tool.link_tickets(primary_key, key)

            # Analyze ticket and add metadata
            if analysis := await self.analyze_ticket(primary_data):
                comment = "\n".join(
                    f"{k}: {v}" for k, v in analysis.items() if v is not None
                )
                await self.jira_tool.add_comment(primary_key, comment)

            return f"Successfully triaged ticket {ticket_number}"
        except Exception as e:
            logger.error(f"Error triaging ticket: {e}", exc_info=True)
            return f"Error triaging ticket: {str(e)}"
