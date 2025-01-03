import concurrent.futures
import json
import os
from typing import Any

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import tool
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_openai import ChatOpenAI
from logger import logger
from utils import (
    add_jira_comment,
    extract_tag_helper,
    get_all_tickets,
    get_ticket_data,
    link_jira_tickets,
)

# Load prompts from JSON files
with open("utils/system_prompts.json") as f:
    system_prompts = json.load(f)
with open("utils/example_prompts.json") as f:
    example_prompts = json.load(f)

# Initialize the LLM
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")


class LLMTask:
    def __init__(
        self, system_prompt: str, examples: list[dict[str, str]], llm: Any
    ) -> None:
        self.system_prompt = system_prompt
        self.examples = examples
        self.llm = llm

    def construct_prompt(self) -> ChatPromptTemplate:
        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=self.examples,
        )
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )

    def run_llm(self, input_text: str) -> str:
        """Run the LLM chain with the given input."""
        try:
            logger.debug(f"Running LLM with input: {input_text}")
            chain = self.construct_prompt() | self.llm
            result = chain.invoke({"input": input_text})
            logger.debug(f"LLM result: {result}")
            return str(result)
        except Exception as e:
            logger.error(f"Error running LLM: {e}", exc_info=True)
            raise


product_model = LLMTask(
    system_prompts.get("system_prompt_product"),
    example_prompts.get("examples_product"),
    llm,
)
linking_model = LLMTask(
    system_prompts.get("system_prompt_linking"),
    example_prompts.get("examples_linking"),
    llm,
)


def check_issue_and_link_helper(args: tuple[str, str, str, str]) -> bool:
    key, data, primary_issue_key, primary_issue_data = args
    logger.debug(f"Checking issue match between {key} and {primary_issue_key}")
    if key != primary_issue_key and llm_check_ticket_match(primary_issue_data, data):
        logger.info(f"Found matching issues: {key} and {primary_issue_key}")
        link_jira_tickets(primary_issue_key, key)
    return True


def find_related_tickets(
    primary_issue_key: str, primary_issue_data: str, issues: dict[str, str]
) -> None:
    args = [
        (key, data, primary_issue_key, primary_issue_data)
        for key, data in issues.items()
    ]
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count()) as executor:
        executor.map(check_issue_and_link_helper, args)


def llm_check_ticket_match(ticket1: str, ticket2: str) -> bool:
    llm_result = linking_model.run_llm(
        f"<ticket1>{ticket1}<ticket1><ticket2>{ticket2}<ticket2>"
    )
    if (result := extract_tag_helper(llm_result)) and (result == "True"):
        return True
    return False


def user_stories_acceptance_criteria_priority(
    primary_issue_key: str, primary_issue_data: str
) -> None:
    if llm_result := product_model.run_llm(
        f"<description>{primary_issue_data}<description>"
    ):
        logger.info(f"LLM result: {llm_result}")
        user_stories = extract_tag_helper(llm_result, "user_stories") or ""
        acceptance_criteria = (
            extract_tag_helper(llm_result, "acceptance_criteria") or ""
        )
        priority = extract_tag_helper(llm_result, "priority") or ""
        thought = extract_tag_helper(llm_result, "thought") or ""
        comment = f"user_stories: {user_stories}\nacceptance_criteria: {acceptance_criteria}\npriority: {priority}\nthought: {thought}"
        add_jira_comment(primary_issue_key, comment)


@tool
def triage(ticket_number: str) -> str:
    """triage a given ticket and link related tickets"""
    ticket_number = str(ticket_number)
    all_tickets = get_all_tickets()
    primary_issue_key, primary_issue_data = get_ticket_data(ticket_number)
    if primary_issue_key and primary_issue_data:
        find_related_tickets(primary_issue_key, primary_issue_data, all_tickets)
        user_stories_acceptance_criteria_priority(primary_issue_key, primary_issue_data)
    return "Task complete"


class LoggingCallbackHandler(BaseCallbackHandler):
    def on_llm_start(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("Starting LLM")

    def on_llm_end(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("LLM finished")

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        logger.error(f"LLM error: {error}")

    def on_chain_start(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("Starting chain")

    def on_chain_end(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("Chain finished")

    def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        logger.error(f"Chain error: {error}")

    def on_tool_start(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("Starting tool")

    def on_tool_end(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("Tool finished")

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        logger.error(f"Tool error: {error}")


jira = JiraAPIWrapper()
toolkit = JiraToolkit.from_jira_api_wrapper(jira)
tools = toolkit.get_tools() + [triage]

# Get tool names for the prompt
tool_names = [tool.name for tool in tools]

# Create the prompt for the agent
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=(
                "You are a helpful AI assistant that helps with Jira tasks. "
                "You have access to tools that can help you interact with Jira. "
                "Think through each request step by step and use the appropriate tools when needed."
            )
        ),
        HumanMessage(content="{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Initialize the agent with proper configuration
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,
    early_stopping_method="generate",
    callbacks=[LoggingCallbackHandler()],
)
