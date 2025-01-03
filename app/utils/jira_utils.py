import re

from langchain_community.utilities.jira import JiraAPIWrapper
from logger import logger

jira = JiraAPIWrapper()


def get_all_tickets() -> dict[str, str]:
    """Get all tickets from Jira"""
    try:
        issues = jira.get_issues()
        return {
            issue.key: f"{issue.fields.summary}\n{issue.fields.description}"
            for issue in issues
        }
    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        return {}


def get_ticket_data(ticket_number: str) -> tuple[str | None, str | None]:
    """Get data for a specific ticket"""
    try:
        issue = jira.get_issue(ticket_number)
        return issue.key, f"{issue.fields.summary}\n{issue.fields.description}"
    except Exception as e:
        logger.error(f"Error getting ticket data: {e}")
        return None, None


def link_jira_issue(from_issue: str, to_issue: str) -> bool:
    """Link two Jira issues"""
    try:
        jira.create_issue_link("Relates", from_issue, to_issue)
        return True
    except Exception as e:
        logger.error(f"Error linking issues: {e}")
        return False


def add_jira_comment(issue_key: str, comment: str) -> bool:
    """Add a comment to a Jira issue"""
    try:
        jira.add_comment(issue_key, comment)
        return True
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        return False


def extract_tag_helper(text: str, tag: str | None = None) -> str | None:
    """Extract content from XML-like tags"""
    try:
        pattern = f"<{tag}>(.*?)</{tag}>" if tag else "<.*?>(.*?)</.*?>"
        if match := re.search(pattern, text, re.DOTALL):
            return match.group(1).strip()
        return None
    except Exception as e:
        logger.error(f"Error extracting tag: {e}")
        return None
