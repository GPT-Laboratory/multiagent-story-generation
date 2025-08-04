import os
import random
import re
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse
import requests


load_dotenv()


# Load environment variables from .env file
# api_keys = [os.getenv(f"API-KEY{i}") for i in range(1, 4)]
api_keys = [os.getenv(f"API-KEY{i}") for i in range(1, 4)]
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("API-KEY1")
url = OPENAI_URL
headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

headers["Authorization"] = f"Bearer {OPENAI_API_KEY}"



def parse_for_upgrade_story(text_response):
    """Parses AI response to extract structured user stories, including suggestions."""
    pattern = re.compile(
        r"- \*\*User Story:\*\* (.*?)\n\n"
        r"- \*\*Epic:\*\* (.*?)\n\n"
        r"- \*\*Description:\*\* (.*?)(?=\n- \*\*Suggestion:\*\*|\Z)",
        re.DOTALL
    )

    suggestion_pattern = re.compile(r"- \*\*Suggestion:\*\* (.*)", re.DOTALL)

    matches = pattern.findall(text_response)
    suggestion_match = suggestion_pattern.search(text_response)

    user_stories = []

    for match in matches:
        user_stories.append({
            "user_story": match[0].strip(),
            "epic": match[1].strip(),
            "description": match[2].strip(),
            "suggestion": suggestion_match.group(1).strip() if suggestion_match else "No suggestions provided",
        })

    if not user_stories:
        user_stories.append({
            "user_story": "User story not provided",
            "epic": "Epic not provided",
            "description": "Description not provided",
            "suggestion": "Suggestion not provided",
        })

    return user_stories


async def upgrade_story(request: Request):
    data = await request.json()
    prompt = data.get("prompt")
    user_story = data.get("user_story")
    # suggestion = data.get("suggestion")
    description = data.get("description")
    epic = data.get("epic")
    agent1 = data.get("agent1")

    print("Prompt:", prompt)  # Debugging
    # print("User Story:", user_story, agent1, description, epic)  # Debugging

    if not prompt:
        return JSONResponse({"error": "Missing prompt or user story"}, status_code=400)

    instructions = (
        "You are an AI that upgrades user stories based on the given prompt. "
        + prompt +
        f"Carefully analyze the prompt and then apply necessary improvements to the provided user story. these are the provided user story details  {user_story} and {epic} and {description} and  {agent1}  \n\n"
        "Strictly provide your response in the following format:\n\n"
        "- **User Story:** As a <role>, I want to <action>, in order to <benefit>.\n"
        "- **Epic:** <epic> (This epic may encompass multiple related user stories)\n"
        "- **Description:** Detailed and clear acceptance criteria that define the success of the user story, "
        "particularly in achieving MVP functionality and supporting the overall vision.\n"
        "- **Suggestion:** \n"
        "    The role providing the suggestion.\n\n"
        "Ensure the upgraded user story aligns with the project vision and MVP requirements."
    )

    post_data = {
        "model": "gpt-4o",  # Change model if needed
        "messages": [
                {"role": "system", "content": f"You are a expert of a user stories generator."},
                {"role": "user", "content": instructions},
            ],
        "temperature": 0.7
    }

    try:
        response = requests.post(OPENAI_URL, json=post_data, headers=headers, timeout=30)

        print("Response:", response.text)  # Debugging

        if response.status_code == 200:
            completion = response.json()
            upgraded_story = completion["choices"][0]["message"]["content"]
            # Parse structured response
            structured_response = parse_for_upgrade_story(upgraded_story)
            return JSONResponse({"upgraded_story": structured_response})
        else:
            return JSONResponse({"error": f"OpenAI API Error: {response.text}"}, status_code=response.status_code)

    except requests.exceptions.RequestException as e:
        return JSONResponse({"error": f"Request failed: {str(e)}"}, status_code=500)




