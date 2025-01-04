import os
from typing import Optional

import requests

import mesop as me

# Configuration
DOCKER_RUNNING = os.environ.get("DOCKER_RUNNING", "false").lower() == "true"
BASE_URL = "http://api:8000/" if DOCKER_RUNNING else "http://localhost:8000/"


def get_project_key() -> Optional[str]:
    """Get and validate project key from environment."""
    project_key = os.environ.get("PROJECT_KEY")
    if not project_key:
        print("WARNING: PROJECT_KEY not set in environment")
        return None

    try:
        # Verify project key with API
        print(f"Validating project key: {project_key}")
        response = requests.get(f"{BASE_URL}api/jira/projects")
        print(f"API Response Status: {response.status_code}")

        if response.status_code == 200:
            projects = response.json()
            print(f"Available projects: {projects}")

            if project_key not in projects:
                print(f"WARNING: Project {project_key} not found in available projects")
                return None

            print(f"Successfully validated project key: {project_key}")
            return project_key
        else:
            print(
                f"ERROR: Failed to fetch projects. Status code: {response.status_code}"
            )
            return None

    except Exception as e:
        print(f"ERROR validating project key: {str(e)}")
        return None


PROJECT_KEY = get_project_key()

# Example prompts with project key validation
DEFAULT_PROJECT = "your-project"
EXAMPLE_PROMPTS = [
    f"How many tasks are in status 'DONE' in project {PROJECT_KEY or DEFAULT_PROJECT}?",
    f"Create a new task in project {PROJECT_KEY or DEFAULT_PROJECT} with description 'This is a test'.",
    f"What are the tasks that are in status 'IN PROGRESS' in project {PROJECT_KEY or DEFAULT_PROJECT}?",
    f"Triage the issue {PROJECT_KEY or DEFAULT_PROJECT}-01",
    f"Transition the tasks that are in status 'IN PROGRESS' in project {PROJECT_KEY or DEFAULT_PROJECT} to 'DONE'",
]

print(f"Using project key: {PROJECT_KEY or DEFAULT_PROJECT} for example prompts")


@me.stateclass
class State:
    input: str
    output: str
    in_progress: bool
    project_key: Optional[str] = PROJECT_KEY


if __name__ == "__main__":
    pass
