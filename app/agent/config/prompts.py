"""Prompt templates and configurations for the agent module."""

from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Base system prompts
JIRA_AGENT_SYSTEM_PROMPT = """You are an AI assistant specialized in Jira task management.
Your role is to help users interact with Jira efficiently and effectively.
You have access to various tools that can help you manage Jira tasks.

When handling requests:
1. Think through the request step by step
2. Use appropriate tools to accomplish the task
3. Provide clear, concise responses
4. Handle errors gracefully
5. Always verify the success of your actions

Remember to:
- Be precise with ticket references
- Double-check before making changes
- Provide context in your responses
- Follow Jira best practices"""

TICKET_LINKING_SYSTEM_PROMPT = """You are an AI assistant specialized in analyzing Jira tickets for relationships.
Your task is to determine if two tickets are related and should be linked.

Consider:
1. Similar descriptions or objectives
2. Shared components or systems
3. Dependencies between tasks
4. Common themes or categories

Respond with <result>True</result> if tickets should be linked, <result>False</result> otherwise."""

TICKET_ANALYSIS_SYSTEM_PROMPT = """You are an AI assistant specialized in analyzing Jira tickets.
Your task is to extract key information and suggest improvements.

For each ticket, provide:
1. User stories in standard format
2. Clear acceptance criteria
3. Suggested priority level
4. Analysis rationale

Format your response using appropriate XML tags:
<user_stories>...</user_stories>
<acceptance_criteria>...</acceptance_criteria>
<priority>...</priority>
<thought>...</thought>"""

# Example prompts for few-shot learning
TICKET_LINKING_EXAMPLES = [
    {
        "input": "<ticket1>Implement user authentication\nAdd login and registration functionality</ticket1><ticket2>Add OAuth2 support\nImplement OAuth2 authentication flow</ticket2>",
        "output": "<result>True</result>",
    },
    {
        "input": "<ticket1>Fix CSS bug in header\nHeader alignment is broken in mobile view</ticket1><ticket2>Update database schema\nAdd new columns to user table</ticket2>",
        "output": "<result>False</result>",
    },
]

TICKET_ANALYSIS_EXAMPLES = [
    {
        "input": "<description>Add export to PDF functionality in the reports section</description>",
        "output": """<user_stories>As a user, I want to export my reports to PDF format so that I can share them offline</user_stories>
<acceptance_criteria>1. PDF export button is visible in reports section
2. Exported PDF maintains report formatting
3. PDF includes all report data
4. User receives download prompt when export is complete</acceptance_criteria>
<priority>Medium</priority>
<thought>Feature enhances report sharing capabilities but isn't blocking core functionality</thought>""",
    },
]


# Create prompt templates
def create_agent_prompt() -> ChatPromptTemplate:
    """Create the main agent prompt template."""
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=JIRA_AGENT_SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )


def create_ticket_linking_prompt() -> ChatPromptTemplate:
    """Create the ticket linking prompt template."""
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=TICKET_LINKING_SYSTEM_PROMPT),
            ("human", "{input}"),
        ]
    )


def create_ticket_analysis_prompt() -> ChatPromptTemplate:
    """Create the ticket analysis prompt template."""
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=TICKET_ANALYSIS_SYSTEM_PROMPT),
            ("human", "{input}"),
        ]
    )
