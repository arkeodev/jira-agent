import requests

# local imports
from . import config


def call_jira_agent(request):
    try:
        data = {"request": request}
        if (
            (
                response := requests.post(
                    f"{config.DJANGO_URL}api/jira-agent/", data=data
                )
            )
            and (response.status_code == 200)
            and (output := response.json().get("output"))
        ):
            return f"Request: {request}<br>Output: {output}<br><br>"
    except Exception as e:
        print(f"ERROR call_jira_agent: {e}")


if __name__ == "__main__":
    pass
