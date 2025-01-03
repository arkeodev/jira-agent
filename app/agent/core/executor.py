"""Agent executor implementation."""
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import BasePromptTemplate
from langchain_openai import ChatOpenAI

from ..config.prompts import create_agent_prompt
from ..config.settings import settings
from ..llm.models import get_llm
from .base import BaseAgent


class JiraAgent(BaseAgent):
    """Agent for handling Jira-related tasks."""

    def __init__(
        self,
        tools: List[BaseTool],
        callbacks: Optional[List[BaseCallbackHandler]] = None,
        llm: Optional[ChatOpenAI] = None,
        prompt: Optional[BasePromptTemplate] = None,
    ) -> None:
        """Initialize the Jira agent.

        Args:
            tools: List of tools available to the agent
            callbacks: Optional list of callback handlers
            llm: Optional LLM override
            prompt: Optional prompt template override
        """
        super().__init__(
            llm=llm or get_llm(),
            tools=tools,
            prompt=prompt or create_agent_prompt(),
            callbacks=callbacks,
            max_iterations=settings.agent.max_iterations,
            early_stopping_method=settings.agent.early_stopping_method,
        )

    def create_agent(self) -> Any:
        """Create the OpenAI functions agent.

        Returns:
            The created agent
        """
        return create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )

    def create_executor(self) -> AgentExecutor:
        """Create the agent executor.

        Returns:
            The configured agent executor
        """
        return AgentExecutor(
            agent=self.create_agent(),
            tools=self.tools,
            callbacks=self.callbacks,
            max_iterations=self.max_iterations,
            early_stopping_method=self.early_stopping_method,
            handle_parsing_errors=settings.agent.handle_parsing_errors,
            verbose=settings.agent.verbose,
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with the given input.

        Args:
            input_data: The input data for the agent

        Returns:
            The agent's response
        """
        result = await self.executor.ainvoke(input_data)
        if not isinstance(result, dict):
            return {"output": str(result)}
        return result
