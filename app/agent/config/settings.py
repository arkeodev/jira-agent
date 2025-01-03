"""Configuration settings for the agent module."""
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LLMSettings(BaseModel):
    """Settings for the language model."""

    llm_model_name: str = Field(
        default="gpt-3.5-turbo", description="Name of the LLM model to use"
    )
    temperature: float = Field(default=0.0, description="Temperature for LLM sampling")
    max_tokens: Optional[int] = Field(
        default=None, description="Maximum tokens for LLM response"
    )
    top_p: float = Field(default=1.0, description="Top p for nucleus sampling")
    frequency_penalty: float = Field(
        default=0.0, description="Frequency penalty for token generation"
    )
    presence_penalty: float = Field(
        default=0.0, description="Presence penalty for token generation"
    )

    model_config = {"protected_namespaces": ()}


class AgentSettings(BaseModel):
    """Settings for the agent execution."""

    max_iterations: int = Field(
        default=5, description="Maximum number of iterations for agent execution"
    )
    early_stopping_method: str = Field(
        default="generate",
        description="Method to use for early stopping",
    )
    verbose: bool = Field(default=True, description="Whether to enable verbose logging")
    handle_parsing_errors: bool = Field(
        default=True,
        description="Whether to handle parsing errors gracefully",
    )

    model_config = {"protected_namespaces": ()}


class Settings(BaseSettings):
    """Main settings for the agent module."""

    llm: LLMSettings = Field(default_factory=LLMSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    openai_api_key: str = Field(..., description="OpenAI API key")
    jira_api_token: str = Field(..., description="Jira API token")
    jira_username: str = Field(..., description="Jira username")
    jira_instance_url: str = Field(..., description="Jira instance URL")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_nested_delimiter": "__",
        "protected_namespaces": (),
    }


# Create global settings instance
settings = Settings()
