import os

import mesop as me

PROJECT_KEY = os.environ.get("PROJECT_KEY")
DOCKER_RUNNING = os.environ.get("DOCKER_RUNNING", False)

EXAMPLE_PROMPTS = [
    f"How many tasks are in status 'DONE' in project {PROJECT_KEY}?",
    f"Create a new task in project {PROJECT_KEY} with description 'This is a test'.",
    f"What are the tasks that are in status 'IN PROGRESS' in project {PROJECT_KEY}?",
    f"Triage the issue {PROJECT_KEY}-19",
    f"Transition the tasks that are in status 'IN PROGRESS' in project {PROJECT_KEY} to 'DONE'",
]

DJANGO_URL = "http://django:8000/" if DOCKER_RUNNING else "http://localhost:8000/"


@me.stateclass
class State:
    input: str
    output: str
    in_progress: bool


if __name__ == "__main__":
    pass
