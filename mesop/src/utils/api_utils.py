import json

import requests

from . import config


def call_jira_agent(request: str) -> str | None:
    """Call the Jira agent API with proper request format"""
    try:
        # Prepare request data in JSON format
        data = {"request": request}
        headers = {"Content-Type": "application/json"}
        url = f"{config.BASE_URL}api/jira/agent"

        # Log request details
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")

        # Make request to FastAPI endpoint
        response = requests.post(url, data=json.dumps(data), headers=headers)

        # Log response details
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if output := result.get("output"):
                return f"Request: {request}<br>Output: {output}<br><br>"

        # Log error details for debugging
        print(f"API Response: Status={response.status_code}, Content={response.text}")
        return None

    except Exception as e:
        print(f"ERROR call_jira_agent: {e}")
        return None


if __name__ == "__main__":
    pass
