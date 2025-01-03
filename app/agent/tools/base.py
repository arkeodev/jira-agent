"""Base classes for agent tools."""
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from langchain.tools import BaseTool
from logger import logger


class AgentTool(BaseTool, ABC):
    """Base class for all agent tools."""

    def __init__(
        self,
        name: str,
        description: str,
        func: Optional[Callable] = None,
        return_direct: bool = False,
        verbose: bool = False,
    ) -> None:
        """Initialize the agent tool.

        Args:
            name: The name of the tool
            description: A description of what the tool does
            func: Optional function to use instead of _run
            return_direct: Whether to return the tool's output directly
            verbose: Whether to enable verbose logging
        """
        super().__init__(
            name=name,
            description=description,
            func=func,
            return_direct=return_direct,
            verbose=verbose,
        )

    def _before_run(self, *tool_args: Any, **tool_kwargs: Any) -> None:
        """Hook called before tool execution."""
        logger.debug(
            f"Running tool {self.name}",
            extra={
                "tool_name": self.name,
                "tool_args": tool_args,
                "tool_kwargs": tool_kwargs,
            },
        )

    def _after_run(self, result: Any) -> None:
        """Hook called after successful tool execution."""
        logger.debug(
            f"Tool {self.name} completed",
            extra={
                "tool_name": self.name,
                "result": result,
            },
        )

    def _on_error(self, error: Exception) -> None:
        """Hook called when tool execution fails."""
        logger.error(
            f"Tool {self.name} failed",
            extra={
                "tool_name": self.name,
                "error": str(error),
                "error_type": type(error).__name__,
            },
            exc_info=True,
        )

    @abstractmethod
    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Run the tool asynchronously."""
        pass

    async def arun(self, *args: Any, **kwargs: Any) -> Any:
        """Run the tool with logging and error handling.

        Args:
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool

        Returns:
            The tool's output

        Raises:
            Exception: If tool execution fails
        """
        try:
            self._before_run(*args, **kwargs)
            result = await self._arun(*args, **kwargs)
            self._after_run(result)
            return result
        except Exception as e:
            self._on_error(e)
            raise
