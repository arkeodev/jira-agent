import concurrent.futures
import json
import os
from typing import Any

from langchain.agents import AgentType, initialize_agent
from langchain.tools import tool
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import OpenAI
from logger import logger
from utils import jira_utils

# Load prompts from JSON files
with open("utils/system_prompts.json") as f:
    system_prompts = json.load(f)
with open("utils/example_prompts.json") as f:
    example_prompts = json.load(f)

llm = OpenAI(temperature=0)


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
        chain = self.construct_prompt() | self.llm
        result = chain.invoke({"input": input_text})
        return str(result)


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
    if key != primary_issue_key and llm_check_ticket_match(primary_issue_data, data):
        jira_utils.link_jira_issue(primary_issue_key, key)
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
    if (result := jira_utils.extract_tag_helper(llm_result)) and (result == "True"):
        return True
    return False


def user_stories_acceptance_criteria_priority(
    primary_issue_key: str, primary_issue_data: str
) -> None:
    if llm_result := product_model.run_llm(
        f"<description>{primary_issue_data}<description>"
    ):
        logger.info(f"LLM result: {llm_result}")
        user_stories = jira_utils.extract_tag_helper(llm_result, "user_stories") or ""
        acceptance_criteria = (
            jira_utils.extract_tag_helper(llm_result, "acceptance_criteria") or ""
        )
        priority = jira_utils.extract_tag_helper(llm_result, "priority") or ""
        thought = jira_utils.extract_tag_helper(llm_result, "thought") or ""
        comment = f"user_stories: {user_stories}\nacceptance_criteria: {acceptance_criteria}\npriority: {priority}\nthought: {thought}"
        jira_utils.add_jira_comment(primary_issue_key, comment)


@tool
def triage(ticket_number: str) -> str:
    """triage a given ticket and link related tickets"""
    ticket_number = str(ticket_number)
    all_tickets = jira_utils.get_all_tickets()
    primary_issue_key, primary_issue_data = jira_utils.get_ticket_data(ticket_number)
    if primary_issue_key and primary_issue_data:
        find_related_tickets(primary_issue_key, primary_issue_data, all_tickets)
        user_stories_acceptance_criteria_priority(primary_issue_key, primary_issue_data)
    return "Task complete"


jira = JiraAPIWrapper()
toolkit = JiraToolkit.from_jira_api_wrapper(jira)
agent = initialize_agent(
    toolkit.get_tools() + [triage],
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=5,
    return_intermediate_steps=True,
)
