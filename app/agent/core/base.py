"""Base classes and interfaces for agent implementations."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import BasePromptTemplate
from langchain_openai import ChatOpenAI


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(
        self,
        llm: ChatOpenAI,
        tools: List[BaseTool],
        prompt: BasePromptTemplate,
        callbacks: Optional[List[BaseCallbackHandler]] = None,
        max_iterations: int = 5,
        early_stopping_method: str = "generate",
    ) -> None:
        """Initialize the base agent.

        Args:
            llm: The language model to use
            tools: List of tools available to the agent
            prompt: The prompt template for the agent
            callbacks: Optional list of callback handlers
            max_iterations: Maximum number of iterations for the agent
            early_stopping_method: Method to use for early stopping
        """
        self.llm = llm
        self.tools = tools
        self.prompt = prompt
        self.callbacks = callbacks or []
        self.max_iterations = max_iterations
        self.early_stopping_method = early_stopping_method
        self._executor: Optional[AgentExecutor] = None

    @abstractmethod
    def create_agent(self) -> Any:
        """Create the specific agent implementation."""
        pass

    @abstractmethod
    def create_executor(self) -> AgentExecutor:
        """Create the agent executor."""
        pass

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with the given input.

        Args:
            input_data: The input data for the agent

        Returns:
            The agent's response
        """
        pass

    @property
    def executor(self) -> AgentExecutor:
        """Get or create the agent executor.

        Returns:
            The agent executor instance
        """
        if self._executor is None:
            self._executor = self.create_executor()
        return self._executor
