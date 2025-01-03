import re

from langchain_community.utilities.jira import JiraAPIWrapper
from logger import logger

jira = JiraAPIWrapper()


def get_all_tickets() -> dict[str, str]:
    """Get all tickets from Jira"""
    try:
        logger.debug("Fetching all tickets from Jira")
        issues = jira.get_issues()
        result = {
            issue.key: f"{issue.fields.summary}\n{issue.fields.description}"
            for issue in issues
        }
        logger.debug(f"Found {len(result)} tickets")
        return result
    except Exception as e:
        logger.error(f"Error getting tickets: {e}", exc_info=True)
        return {}


def get_ticket_data(ticket_number: str) -> tuple[str | None, str | None]:
    """Get data for a specific ticket"""
    try:
        logger.debug(f"Fetching data for ticket: {ticket_number}")
        issue = jira.get_issue(ticket_number)
        result = (issue.key, f"{issue.fields.summary}\n{issue.fields.description}")
        logger.debug(f"Retrieved ticket data: {result[0]}")
        return result
    except Exception as e:
        logger.error(f"Error getting ticket data: {e}", exc_info=True)
        return None, None


def link_jira_tickets(from_issue: str, to_issue: str) -> bool:
    """Link two Jira issues"""
    try:
        logger.debug(f"Linking issues: {from_issue} -> {to_issue}")
        jira.create_issue_link("Relates", from_issue, to_issue)
        logger.info(f"Successfully linked issues: {from_issue} -> {to_issue}")
        return True
    except Exception as e:
        logger.error(f"Error linking issues: {e}", exc_info=True)
        return False


def add_jira_comment(issue_key: str, comment: str) -> bool:
    """Add a comment to a Jira issue"""
    try:
        logger.debug(f"Adding comment to issue {issue_key}: {comment}")
        jira.add_comment(issue_key, comment)
        logger.info(f"Successfully added comment to issue {issue_key}")
        return True
    except Exception as e:
        logger.error(f"Error adding comment: {e}", exc_info=True)
        return False


def extract_tag_helper(text: str, tag: str | None = None) -> str | None:
    """Extract content from XML-like tags"""
    try:
        pattern = f"<{tag}>(.*?)</{tag}>" if tag else "<.*?>(.*?)</.*?>"
        logger.debug(f"Extracting tag {tag if tag else 'any'} from text: {text}")
        if match := re.search(pattern, text, re.DOTALL):
            result = match.group(1).strip()
            logger.debug(f"Extracted content: {result}")
            return result
        logger.debug("No matching tag found")
        return None
    except Exception as e:
        logger.error(f"Error extracting tag: {e}", exc_info=True)
        return None
