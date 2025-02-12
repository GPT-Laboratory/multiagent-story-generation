# helpers.py

import io
import re
import random
import logging
import os
import csv
from openai import OpenAI
import requests
from starlette.datastructures import UploadFile
import httpx
from httpx import Timeout, AsyncClient
import asyncio
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState
import pdfplumber

GPT_API_KEY = os.getenv("GPT_API_KEY")

from agent import OPENAI_URL
LLAMA_URL="https://api.groq.com/openai/v1/chat/completions"

# from app import send_to_llm

# Load environment variables from .env file
api_keys = [os.getenv(f"API-KEY{i}") for i in range(1, 4)]
llama_keys = [os.getenv(f"LLAMA-key{i}") for i in range(1, 3)]

print("API Keys: in ", api_keys)
print("GROQ keys : in ", llama_keys)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_random_temperature(low=0.1, high=0.7):
    return random.uniform(low, high)

async def estimate_ahp(data, websocket, model, topic_response, context_response):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }
    
    prioritize_prompt = construct_ahp_prompt(data, topic_response, context_response)
    estimated_factors = await send_to_llm(prioritize_prompt, headers, model)
    await stream_response_word_by_word(websocket, estimated_factors, "Final Prioritization")
    
    prioritized_stories = parse_prioritized_stories(estimated_factors)
    logger.info(f"Prioritized Stories:\n{prioritized_stories}")
    
    enriched_stories = enrich_original_stories_with_ahp(data['stories'], prioritized_stories)
    logger.info(f"Enriched Stories:\n{enriched_stories}")

    return enriched_stories

# def construct_ahp_prompt(data):
#     stories_formatted = '\n'.join([
#         f"- Story ID {story['key']}: '{story['user_story']}' {story['epic']})"
#         for story in data['stories']
#     ])
    
#     prompt = (
#         "You are a helpful assistant. Using the Analytic Hierarchy Process (AHP), prioritize the following user stories based on their relative importance.\n\n"
#         f"Here are the stories:\n{stories_formatted}\n\n"
#         "Please provide the following factors for each story on a scale of 1 to 10, where 1 represents the lowest and 10 represents the highest:\n"
#         "- Business Value (BV): The importance of this story to the business or stakeholders.\n"
#         "- Effort Required (ER): The amount of effort needed to complete this story.\n"
#         "- Dependencies (D): The extent to which this story depends on other factors or stories.\n\n"
#         "Then calculate the overall weight (W) and overall score (OS) using the following formula:\n"
#         "- W = (BV + ER + D) / 3\n"
#         "- OS = W\n\n"
#         "Return the list of stories in the following format:\n\n"
#         "### Story ID X: <Story Title>\n"
#         "- BV: <value>\n"
#         "- ER: <value>\n"
#         "- D: <value>\n"
#         "- W: <value>\n"
#         "- OS: <value>\n\n"
#         "Please maintain this exact format so that the values can be easily parsed."
#     )
    
#     return prompt

def construct_ahp_prompt(data, topic_response, context_response):
    stories_formatted = '\n'.join([
        f"- Story ID {story['key']}: '{story['user_story']}' (Epic: '{story['epic']}') - {story['description']}"
        for story in data['stories']
    ])

    topic_response_direct = '\n'.join(topic_response)
    context_response_direct = '\n'.join(context_response)

    print(stories_formatted)
    print(topic_response_direct)
    print(context_response_direct)
    
    prompt = (
        "You are a helpful assistant. Using the Analytic Hierarchy Process (AHP), prioritize the following user stories based on their relative importance.\n\n"
        f"Here are the stories:\n{stories_formatted}\n\n"
        "Previously, the following points were discussed regarding prioritization:\n"
        f"{topic_response_direct}\n\n"
        "Additionally, here is the context from prior discussions:\n"
        f"{context_response_direct}\n\n"
        "Please provide the following factors for each story on a scale of 1 to 10, where 1 represents the lowest and 10 represents the highest:\n"
        "- Business Value (BV): The importance of this story to the business or stakeholders.\n"
        "- Effort Required (ER): The amount of effort needed to complete this story.\n"
        "- Dependencies (D): The extent to which this story depends on other factors or stories.\n\n"
        "Then calculate the overall weight (W) and overall score (OS) using the following formula:\n"
        "- W = (BV + ER + D) / 3\n"
        "- OS = W\n\n"
        "Return the list of stories in the following format:\n\n"
        "### Story ID X: <Story Title>\n"
        "- BV: <value>\n"
        "- ER: <value>\n"
        "- D: <value>\n"
        "- W: <value>\n"
        "- OS: <value>\n\n"
        "For each story, provide a detailed explanation of why it received the allocated values. What is the main reason behind its prioritization? Make sure to include a complete explanation for every story."
    )
    
    return prompt


# async def send_to_llm(prompt, headers, model, timeout=100):
#     if model.startswith("llama3") or model == "mixtral-8x7b-32768" or model == "deepseek-r1-distill-llama-70b-specdec":
#         url = LLAMA_URL
#         headers["Authorization"] = f"Bearer {random.choice(llama_keys)}"
#     elif model == "deepseek-r1:7b":
#         # Initialize OpenAI client for DeepSeek model
#         client = OpenAI(
#             base_url='https://gptlab.rd.tuni.fi/GPT-Lab/resources/GPU-farmi-001/v1',
#             api_key=GPT_API_KEY
#         )

#         response = client.chat.completions.create(
#             model=model,
#             messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]
#         )

#         generated_content = response.choices[0].message.content
#         print(f"Generated response using DeepSeek: {generated_content}")
#         return generated_content
#     else:
#         url = OPENAI_URL
#         headers["Authorization"] = f"Bearer {random.choice(api_keys)}"
    
#     post_data = {
#         "model": model,
#         "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
#         "temperature": 0.7
#     }
    
#     response = requests.post(url, json=post_data, headers=headers, timeout=timeout)
    
#     if response.status_code == 200:
#         completion = response.json()
#         completion_text = completion['choices'][0]['message']['content']
#         return completion_text
#     else:
#         raise Exception("Failed to process the request with OpenAI")
    
async def send_to_llm(prompt, headers, model, timeout=100):
    format_instruction = """
    Please format your response in the following way:

    ```
    - Story ID 1: 10 dollars
    - Story ID 2: 8 dollars
    - Story ID 3: 12 dollars
    - Story ID 4: 5 dollars
    ```
    
    Ensure:
    1. The story IDs follow the format: `- Story ID X: Y dollars`
    2. No extra explanations or calculations in the response.
    3. The sum of all allocated dollars should be exactly 100.
    """

    if model.startswith("llama3") or model == "mixtral-8x7b-32768" or model == "deepseek-r1-distill-llama-70b-specdec":
        url = LLAMA_URL
        headers["Authorization"] = f"Bearer {random.choice(llama_keys)}"
    elif model == "deepseek-r1:7b":
        client = OpenAI(
            base_url='https://gptlab.rd.tuni.fi/GPT-Lab/resources/GPU-farmi-001/v1',
            api_key=GPT_API_KEY
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "system", "content": format_instruction},  # <-- Add format instruction
                {"role": "user", "content": prompt}
            ]
        )

        generated_content = response.choices[0].message.content
        print(f"Generated response using DeepSeek: {generated_content}")
        return generated_content
    else:
        url = OPENAI_URL
        headers["Authorization"] = f"Bearer {random.choice(api_keys)}"
    
    post_data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "system", "content": format_instruction},  # <-- Add format instruction
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(url, json=post_data, headers=headers, timeout=timeout)
    
    if response.status_code == 200:
        completion = response.json()
        completion_text = completion['choices'][0]['message']['content']
        return completion_text
    else:
        raise Exception("Failed to process the request with OpenAI")



async def send_to_llm_for_img(prompt, image_base64, headers, model, timeout=100):
    if model.startswith("llama3") or model == "mixtral-8x7b-32768":
        url = LLAMA_URL
        headers["Authorization"] = f"Bearer {random.choice(llama_keys)}"
    else:
        url = OPENAI_URL
        headers["Authorization"] = f"Bearer {random.choice(api_keys)}"
    
    post_data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
            ]}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(url, json=post_data, headers=headers, timeout=timeout)
    
    if response.status_code == 200:
        completion = response.json()
        return completion["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Failed to process the request: {response.text}")

def parse_prioritized_stories(completion_text):
    pattern = re.compile(
        r"### Story ID (\d+): ([^\n]+)\n"
        r"- BV: (\d+)\n"
        r"- ER: (\d+)\n"
        r"- D: (\d+)\n"
        r"- W: ([0-9.]+)\n"
        r"- OS: ([0-9.]+)"
    )

    prioritized_stories = []

    for match in pattern.finditer(completion_text):
        story_id, story_title, bv, er, d, weight, os = match.groups()
        prioritized_stories.append({
            "ID": int(story_id),
            "user_story": story_title,
            "BV": int(bv),
            "ER": int(er),
            "D": int(d),
            "W": float(weight),
            "OS": float(os),
        })

    # Sort the stories by overall score in descending order
    prioritized_stories.sort(key=lambda x: x["OS"], reverse=True)
    return prioritized_stories

def enrich_original_stories_with_ahp(original_stories, prioritized_stories):
    for story in original_stories:
        story_id = story['key']
        priority_data = next((item for item in prioritized_stories if item["ID"] == story_id), None)
        if priority_data:
            story.update(priority_data)
        else:
            story.update({
                "BV": 0,
                "ER": 0,
                "D": 0,
                "W": 0,
                "OS": 0,
                "priority": float('inf')
            })
            logger.warning(f"Story ID {story_id} not found in prioritized stories")

    enriched_stories = sorted(original_stories, key=lambda x: x.get('OS', 0), reverse=True)
    return enriched_stories

# End of AHP      


def construct_greetings_prompt(prioritization_technique):
    prompt = (
        "PO: Hi QA and QA, hope you're both having a great day!\n"
        "QA: Hi PO, hi Developer! I’m doing well, thanks.\n"
        "Developer: Hey PO, hey QA! All good here.\n\n"
        "PO: We have some user stories pending in our backlog that we need to prioritize.\n"
        f"QA: Let's use the {prioritization_technique} technique for prioritization.\n"
        "Developer: Sounds good to me. Let's dive in."
    )
    return prompt

# def construct_topic_prompt(stories, technique):
#     stories_formatted = construct_stories_formatted(stories)
#     prompt = (
#         "PO, QA, and Developer, please discuss the following user stories and introduce the topic of the requirements:\n\n"
#         f"{stories_formatted}\n\n"
#         f"Please consider the prioritization technique: {technique}.\n\n"
#     )
#     return prompt

# def construct_context_prompt(stories, technique):
#     stories_formatted = construct_stories_formatted(stories)
#     prompt = (
#         "PO, QA, and Developer, please discuss the context and relevance of the following user stories:\n\n"
#         f"{stories_formatted}\n\n"
#         f"Please consider the prioritization technique: {technique}.\n\n "
#     )
#     return prompt

# def construct_batch_100_dollar_prompt(data):
#     stories_formatted = '\n'.join([
#         f"- Story ID {story['key']}: '{story['user_story']}' {story['epic']} {story['description']}"
#         for story in data['stories']
#     ])

#     print(stories_formatted)
    
#     prompt = (
#         "You are a helpful assistant trained in prioritization techniques. "
#         "We need to prioritize the following user stories by distributing 100 dollars (points) among them. "
#         "The more important a story, the more dollars it should receive. "
#         "Here are the stories:\n\n"
#         f"{stories_formatted}\n\n"
#         "Please distribute 100 dollars across these stories. Each dollar represents the relative importance of that story. "
#         "Make sure the total adds up to 100 dollars. Format the output as:\n"
#         "- Story ID X: Y dollars\n"
#         "- Story ID Z: W dollars"
#     )
    
#     return prompt

def construct_topic_prompt(stories, technique):
    stories_formatted = construct_stories_formatted(stories)
    prompt = (
        "PO, QA, and Developer, please introduce the topic of the requirements for the following user stories:\n\n"
        f"{stories_formatted}\n\n"
        f"Use the prioritization technique: {technique} to prioritize, and discuss relevant points only.\n\n"
    )
    return prompt

def construct_context_prompt(stories, technique):
    stories_formatted = construct_stories_formatted(stories)
    prompt = (
        "PO, QA, and Developer, please discuss the context and relevance of the following user stories:\n\n"
        f"{stories_formatted}\n\n"
        f"Use the prioritization technique: {technique} to prioritize, and discuss relevant points only.\n\n"
    )
    return prompt

def construct_batch_100_dollar_prompt(data, qa_response, dev_response, po_response):
    # Ensure story IDs start from 1
    stories_formatted = '\n'.join([
        f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    qa_response_direct = '\n'.join(qa_response)
    dev_response_direct = '\n'.join(dev_response)
    po_response_direct = '\n'.join(po_response)

    print(stories_formatted)
    print(qa_response_direct)
    print(dev_response_direct)
    print(po_response_direct)
    
    # prompt = (
    # "You are the Manager agent, the head of the team responsible for prioritizing user stories by distributing 100 dollars (points) among them. "
    # "You will base your prioritization on the combined input from three agents: QA (focused on quality and testing aspects), Developer (focused on technical context and feasibility), and Product Owner (focused on business and client needs).\n\n"
    # "To make a balanced decision, you will:\n"
    # "- Aggregate the feedback from each agent, averaging their inputs.\n"
    # "- Consider the complexity, importance, and alignment with the project’s vision and MVP goals.\n"
    # "- Provide an explanation for the prioritization based on these factors.\n\n"
    # "Here are the user stories:\n\n"
    # f"{stories_formatted}\n\n"
    # "Each role has provided their input based on their expertise:\n\n"
    # f"QA's input:\n{qa_response_direct}\n\n"
    # f"Developer's context:\n{dev_response_direct}\n\n"
    # f"Product Owner's perspective:\n{po_response_direct}\n\n"
    # "Please distribute 100 dollars across these stories. Each dollar represents the relative importance of that story. "
    # "Make sure the total adds up to 100 dollars. Your response should strictly follow this format:\n"
    # "- Story ID X: Y dollars\n"
    # "- Story ID Z: W dollars\n\n"
    # "After the dollar allocation, provide a summary explanation for the distribution, outlining how the feedback from the three agents, along with complexity and alignment with project goals, influenced the prioritization."
    # )

    prompt = (
    "You are the Manager agent, responsible for prioritizing user stories by distributing exactly 100 dollars among them. "
    "Your prioritization is based on inputs from three agents: QA (focused on quality and testing aspects), Developer (focused on technical feasibility), and Product Owner (focused on business and client needs).\n\n"
    "To make a balanced decision, you will:\n"
    "- Aggregate feedback from each agent, averaging their inputs.\n"
    "- Consider the complexity, importance, and alignment with the project’s vision and MVP goals.\n"
    "- Carefully distribute exactly 100 dollars across these stories. **If your allocation does not add up to 100, adjust and recalculate until the total is exactly 100 dollars.**\n\n"
    "**Important Steps for Exact Calculation**:\n"
    "1. Distribute dollars based on importance. Add up your initial allocation.\n"
    "2. If the sum is more than 100, reduce values incrementally across stories until the total is exactly 100.\n"
    "3. If the sum is less than 100, increase values incrementally across stories until the total is exactly 100.\n"
    "4. Repeat these adjustments as needed until the total equals exactly 100.\n\n"
    "Here are the user stories:\n\n"
    f"{stories_formatted}\n\n"
    "Each role has provided their input based on their expertise:\n\n"
    f"QA's input:\n{qa_response_direct}\n\n"
    f"Developer's context:\n{dev_response_direct}\n\n"
    f"Product Owner's perspective:\n{po_response_direct}\n\n"
    "Please distribute exactly 100 dollars across these stories. Each dollar represents the importance of that story.\n"
    "Your response must strictly follow this format:\n"
    "- Story ID X: Y dollars\n"
    "- Story ID Z: W dollars\n\n"
    "After allocating, **double-check that the total is exactly 100 dollars. If it does not total 100, adjust and verify until it equals exactly 100.**\n\n"
    "The summary should outline how the feedback from the three agents, along with complexity and alignment with project goals, influenced the prioritization."
)

    
    return prompt
   

# def construct_batch_100_dollar_prompt(data, topic_response, context_response):
#     stories_formatted = '\n'.join([
#         f"- Story ID {story['key']}: '{story['user_story']}' {story['epic']} {story['description']}"
#         for story in data['stories']
#     ])

#     topic_response_formatted = '\n'.join([f"- {response}" for response in topic_response])
#     context_response_formatted = '\n'.join([f"- {response}" for response in context_response])

#     print(stories_formatted)
#     print(topic_response_formatted)
#     print(context_response_formatted)
    
#     prompt = (
#         "You are a helpful assistant trained in prioritization techniques. "
#         "We need to prioritize the following user stories by distributing 100 dollars (points) among them. "
#         "The more important a story, the more dollars it should receive. "
#         "Here are the stories:\n\n"
#         f"{stories_formatted}\n\n"
#         "Previously, the following points were discussed regarding prioritization:\n"
#         f"{topic_response_formatted}\n\n"
#         "Additionally, here is the context from prior discussions:\n"
#         f"{context_response_formatted}\n\n"
#         "Please distribute 100 dollars across these stories. Each dollar represents the relative importance of that story. "
#         "Make sure the total adds up to 100 dollars. Format the output as:\n"
#         "- Story ID X: Y dollars\n"
#         "- Story ID Z: W dollars\n\n"
#         "Critique: Explain why the agents prioritize the user stories in this way. What are the reasons behind their prioritization decisions?"
#     )
    
#     return prompt

def parse_100_dollar_response(response_text):
    # pattern = re.compile(r"- Story ID (\d+): .*?(\d+) dollars")
    pattern = re.compile(r"- Story ID (\d+): (\d+) dollars")
    dollar_distribution = []

    for match in pattern.finditer(response_text):
        story_id, dollars = match.groups()
        dollar_distribution.append({
            'story_id': int(story_id),
            'dollars': int(dollars)
        })

    return dollar_distribution

def validate_dollar_distribution(dollar_distribution, stories):
    total_dollars = sum(dist['dollars'] for dist in dollar_distribution)
    story_ids = {story['key'] for story in stories}
    response_story_ids = {dist['story_id'] for dist in dollar_distribution}
    
    return total_dollars == 100 and story_ids == response_story_ids

def enrich_stories_with_dollar_distribution(original_stories, dollar_distribution):
    dollar_dict = {dist['story_id']: dist['dollars'] for dist in dollar_distribution}

    enriched_stories = []
    for story in original_stories:
        story_id = story['key'] + 1 
        story['dollar_allocation'] = dollar_dict.get(story_id, 0)
        enriched_stories.append(story)

    # Sort the enriched stories by dollar_allocation in descending order
    enriched_stories.sort(key=lambda x: x['dollar_allocation'], reverse=True)
    
    return enriched_stories


def enrich_agents_stories_with_dollar_distribution(original_stories, dollar_distribution):
    # Create a dictionary from dollar_distribution for quick lookup
    dollar_dict = {dist['story_id']: dist['dollars'] for dist in dollar_distribution}

    # Enrich each story with dollar allocation
    enriched_stories = []
    for story in original_stories:
        story_id = story['key'] + 1  # Assuming 'key' starts from 0
        story['dollar_allocation'] = dollar_dict.get(story_id, 0)  # Default to 0 if not found
        enriched_stories.append(story)

    # Sort the enriched stories by dollar_allocation in descending order
    enriched_stories.sort(key=lambda x: x['dollar_allocation'], reverse=True)

    # Add all enriched stories to both arrays
    array_one = enriched_stories
    array_two = enriched_stories

    return array_one, array_two




def construct_stories_formatted(stories):
    return '\n'.join([
        f"- Story ID {story['key']}: '{story['user_story']}' {story['epic']} {story['description']}  "
        for story in stories
    ])

def ensure_unique_keys(stories):
    seen = {}
    for story in stories:
        key = story['key']
        if key in seen:
            seen[key] += 1
            story['key'] = f"{key}_{seen[key]}"
        else:
            seen[key] = 0
    return stories


async def estimate_wsjf_final_Prioritization(data, stories, websocket, model):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }
    
    # prioritize_prompt = construct_batch_wsjf_prompt(data, topic_response, context_response)
    #logger.info(f"Prioritize Prompt:\n{prioritize_prompt}")  # Debugging print
    estimated_factors = await send_to_llm(data, headers, model)
    # await stream_response_word_by_word(websocket, estimated_factors, "Final Prioritization")
    #logger.info(f"Estimated Factor:\n{estimated_factors}")

    print("Estimated Factors list: ", estimated_factors)
    
    wsjf_factors = parse_wsjf_response(estimated_factors)
    logger.info(f"wsjf_factors Factor:\n{wsjf_factors}")

    print("WSJF Factors list: ", wsjf_factors)
    

    enriched_stories = enrich_original_stories_with_wsjf_final_prioritization(stories, wsjf_factors)
    logger.info(f"wsjf_factors Factor enrich:\n{enriched_stories}")

    return enriched_stories
    

async def estimate_wsjf(data, stories, websocket, model):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }
    
    # prioritize_prompt = construct_batch_wsjf_prompt(data, topic_response, context_response)
    #logger.info(f"Prioritize Prompt:\n{prioritize_prompt}")  # Debugging print
    estimated_factors = await send_to_llm(data, headers, model)
    # await stream_response_word_by_word(websocket, estimated_factors, "Final Prioritization")
    #logger.info(f"Estimated Factor:\n{estimated_factors}")

    print("Estimated Factors list: ", estimated_factors)
    
    wsjf_factors = parse_wsjf_response(estimated_factors)
    logger.info(f"wsjf_factors Factor:\n{wsjf_factors}")

    print("WSJF Factors list: ", wsjf_factors)
    

    enriched_stories = enrich_original_stories_with_wsjf(stories, wsjf_factors)
    logger.info(f"wsjf_factors Factor enrich:\n{enriched_stories}")

    return enriched_stories
    
# def construct_batch_wsjf_prompt(stories):
#     stories_formatted = '\n'.join([
#         f"- Story ID {story['key']}: '{story['user_story']}' {story['epic']} "
#         for story in stories
#     ])
    
#     prompt = (
#         "You are a helpful assistant trained in WSJF factor estimation. "
#         "For each of the following user stories, please provide estimated numeric values (scale 1 to 10) for the WSJF factors:\n\n"
#         f"Here are the stories:\n{stories_formatted}\n\n"
#         "Please consider the following factors and provide values on a scale of 1 to 10, where 1 represents the lowest impact or effort and 10 represents the highest:\n"
#         "- Business Value (BV): The relative importance of this story to the business or stakeholders.\n"
#         "- Time Criticality (TC): The urgency of delivering this story sooner rather than later.\n"
#         "- Risk Reduction/Opportunity Enablement (RR/OE): The extent to which delivering this story can reduce risks or enable new opportunities.\n"
#         "- Job Size (JS): The amount of effort required to complete this story, typically measured in story points or ideal days.\n\n"
#         "Format the output as:\n"
#         "- Story ID X: (Epic: Y)\n"
#         "  - Business Value (BV): Z\n"
#         "  - Time Criticality (TC): W\n"
#         "  - Risk Reduction/Opportunity Enablement (RR/OE): V\n"
#         "  - Job Size (JS): U\n"
#     )
    
#     return prompt

def construct_batch_wsjf_prompt(stories, topic_response, context_response):
    stories_formatted = '\n'.join([
        f"- Story ID {story['key']}: '{story['user_story']}' (Epic: '{story['epic']}') - {story['description']}"
        for story in stories
    ])
    
    topic_response_direct = '\n'.join(topic_response)
    context_response_direct = '\n'.join(context_response)
    
    #print(stories_formatted)
    #print(topic_response_direct)
    #print(context_response_direct)
    
    prompt = (
        "You are a helpful assistant trained in WSJF factor estimation. "
        "For each of the following user stories, please provide estimated numeric values (scale 1 to 10) for the WSJF factors:\n\n"
        f"Here are the stories:\n{stories_formatted}\n\n"
        "Previously, the following points were discussed regarding prioritization:\n"
        f"{topic_response_direct}\n\n"
        "Additionally, here is the context from prior discussions:\n"
        f"{context_response_direct}\n\n"
        "Please consider the following factors and provide values on a scale of 1 to 10, where 1 represents the lowest impact or effort and 10 represents the highest:\n"
        "- Business Value (BV): The relative importance of this story to the business or stakeholders.\n"
        "- Time Criticality (TC): The urgency of delivering this story sooner rather than later.\n"
        "- Risk Reduction/Opportunity Enablement (RR/OE): The extent to which delivering this story can reduce risks or enable new opportunities.\n"
        "- Job Size (JS): The amount of effort required to complete this story, typically measured in story points or ideal days.\n\n"
        "Format the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Time Criticality (TC): W\n"
        "  - Risk Reduction/Opportunity Enablement (RR/OE): V\n"
        "  - Job Size (JS): U\n\n"
        "For each story, provide a detailed explanation of why it received the allocated values. What is the main reason behind its prioritization? Make sure to include a complete explanation for every story."
    )
    
    return prompt
    

def parse_wsjf_response(response_text):
    pattern = re.compile(
        r"- Story ID (\d+): \(Epic: .+?\)\s*"
        r"- Business Value \(BV\): (\d+)\s*"
        r"- Time Criticality \(TC\): (\d+)\s*"
        r"- Risk Reduction/Opportunity Enablement \(RR/OE\): (\d+)\s*"
        r"- Job Size \(JS\): (\d+)\s*"
        r"- WSJF Score: ([\d.]+)\s*"
    )

    wsjf_factors = []
    
    for match in pattern.finditer(response_text):
        story_id, bv, tc, rr_oe, js, wsjf_score = match.groups()

        wsjf_factors.append({
            'story_id': int(story_id),
            'wsjf_factors': {
                'BV': int(bv),
                'TC': int(tc),
                'RR/OE': int(rr_oe),
                'JS': int(js),
            },
            'wsjf_score': float(wsjf_score)
        })
    
    return wsjf_factors

def validate_wsjf_response(wsjf_factors, stories):
    story_ids = {story['key'] for story in stories}
    response_story_ids = {factor['story_id'] for factor in wsjf_factors}
    
    if story_ids == response_story_ids:
        return True
    return False

# def enrich_original_stories_with_wsjf(original_stories, wsjf_factors):
#     wsjf_dict = {factor['story_id']: factor['wsjf_factors'] for factor in wsjf_factors}
#     logger.info(f"Original stories:\n{original_stories}")
#     logger.info(f"WSJF factors dictionary:\n{wsjf_dict}")

#     enriched_stories = []
#     for story in original_stories:
#         story_id = story['key']
#         if story_id in wsjf_dict:
#             wsjf_data = wsjf_dict[story_id]
#             story['wsjf_factors'] = wsjf_data
#             bv = wsjf_data['BV']
#             tc = wsjf_data['TC']
#             rr_oe = wsjf_data['RR/OE']
#             js = wsjf_data['JS']
#             wsjf_score = (bv + tc + rr_oe) / js if js != 0 else 0  # Prevent division by zero
#             story['wsjf_score'] = wsjf_score
#             story['bv'] = bv
#             story['tc'] = tc
#             story['oe'] = rr_oe
#             story['js'] =  js 

#             logger.info(f"Story ID {story_id} WSJF factors: {wsjf_data}, WSJF score: {wsjf_score}")
#         else:
#             story['wsjf_factors'] = {
#                 'BV': 0,
#                 'TC': 0,
#                 'RR/OE': 0,
#                 'JS': 0
#             }
#             story['wsjf_score'] = 0
#             story['bv'] = 0
#             story['tc'] = 0
#             logger.warning(f"Story ID {story_id} not found in WSJF factors")

#         enriched_stories.append(story)

#     # enriched_stories = sort_stories_by_wsjf_in_place(enriched_stories)
#     sorted_stories = sort_stories_by_wsjf_in_place(enriched_stories)

#     # Return two arrays with the same enriched stories
#     array_one = sorted_stories
#     array_two = sorted_stories
#     # return enriched_stories
#     return array_one, array_two


def enrich_original_stories_with_wsjf(original_stories, wsjf_factors):
    wsjf_dict = {factor['story_id']: factor['wsjf_factors'] for factor in wsjf_factors}
    logger.info(f"Original stories:\n{original_stories}")
    logger.info(f"WSJF factors dictionary:\n{wsjf_dict}")

    enriched_stories = []
    for story in original_stories:
        story_id = story['key']
        if story_id in wsjf_dict:
            wsjf_data = wsjf_dict[story_id]
            story['wsjf_factors'] = wsjf_data
            bv = wsjf_data['BV']
            tc = wsjf_data['TC']
            rr_oe = wsjf_data['RR/OE']
            js = wsjf_data['JS']
            wsjf_score = (bv + tc + rr_oe) / js if js != 0 else 0  # Prevent division by zero
            story['wsjf_score'] = wsjf_score
            story['bv'] = bv
            story['tc'] = tc
            story['oe'] = rr_oe
            story['js'] = js 

            logger.info(f"Story ID {story_id} WSJF factors: {wsjf_data}, WSJF score: {wsjf_score}")
        else:
            story['wsjf_factors'] = {
                'BV': 0,
                'TC': 0,
                'RR/OE': 0,
                'JS': 0
            }
            story['wsjf_score'] = 0
            story['bv'] = 0
            story['tc'] = 0
            logger.warning(f"Story ID {story_id} not found in WSJF factors")

        enriched_stories.append(story)

    # Sort the enriched stories by WSJF score
    sorted_stories = sort_stories_by_wsjf_in_place(enriched_stories)

    # Return two arrays with the same enriched stories
    array_one = sorted_stories
    array_two = sorted_stories

    return array_one, array_two


def enrich_original_stories_with_wsjf_final_prioritization(original_stories, wsjf_factors):
    wsjf_dict = {factor['story_id']: factor['wsjf_factors'] for factor in wsjf_factors}
    logger.info(f"Original stories:\n{original_stories}")
    logger.info(f"WSJF factors dictionary:\n{wsjf_dict}")

    enriched_stories = []
    for story in original_stories:
        story_id = story['key']
        if story_id in wsjf_dict:
            wsjf_data = wsjf_dict[story_id]
            story['wsjf_factors'] = wsjf_data
            bv = wsjf_data['BV']
            tc = wsjf_data['TC']
            rr_oe = wsjf_data['RR/OE']
            js = wsjf_data['JS']
            wsjf_score = (bv + tc + rr_oe) / js if js != 0 else 0  # Prevent division by zero
            story['wsjf_score'] = wsjf_score
            story['bv'] = bv
            story['tc'] = tc
            story['oe'] = rr_oe
            story['js'] = js 

            logger.info(f"Story ID {story_id} WSJF factors: {wsjf_data}, WSJF score: {wsjf_score}")
        else:
            story['wsjf_factors'] = {
                'BV': 0,
                'TC': 0,
                'RR/OE': 0,
                'JS': 0
            }
            story['wsjf_score'] = 0
            story['bv'] = 0
            story['tc'] = 0
            logger.warning(f"Story ID {story_id} not found in WSJF factors")

        enriched_stories.append(story)

    # Sort the enriched stories by WSJF score
    enriched_stories = sort_stories_by_wsjf_in_place(enriched_stories)
    return enriched_stories


def sort_stories_by_wsjf_in_place(enriched_stories):
    return sorted(enriched_stories, key=lambda story: story.get('wsjf_score', 0), reverse=True)

    enriched_sorted_stories = sort_stories_by_wsjf_in_place(enriched_stories)
    logger.info(f"Append and Sorted:\n{enriched_sorted_stories}")
    return enriched_sorted_stories


def save_uploaded_file(upload_folder: str, file: UploadFile):
    # Validate file extensions
    if not file.filename.lower().endswith(('.csv', '.pdf')):
        return None, 'Unsupported file type'

    try:
        # Ensure the upload folder exists
        os.makedirs(upload_folder, exist_ok=True)

        # Save the file
        file_path = os.path.join(upload_folder, file.filename)
        with open(file_path, 'wb') as f:
            f.write(file.file.read())
        return file_path, None
    except Exception as e:
        return None, f"Error saving file: {str(e)}"

def parse_csv_to_json(file_path):
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_data = list(csv_reader)  # Convert CSV file content to a list of dictionaries
    os.remove(file_path)  # Optional: remove the file after processing
    return csv_data

async def extract_text_from_pdf(file: UploadFile):
    try:
        # Read the file content into bytes
        file_bytes = await file.read()
        
        # Use BytesIO to treat the bytes like a file for pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            all_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                    
        # If no text was extracted, raise an error
        if not all_text:
            raise ValueError("No text could be extracted from the PDF.")
        
        return all_text
    except Exception as e:
        # Handle PDF reading/extraction errors
        raise ValueError(f"Error extracting text from PDF: {str(e)}")

#     raise Exception("Failed to get response from OpenAI after multiple attempts")

# Implement MOSCOW Technique 


# MoSCoW Functions

async def estimate_moscow(data, websocket, model, topic_response, context_response):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }
    
    prioritize_prompt = construct_batch_moscow_prompt(data, topic_response, context_response)
    estimated_priorities = await send_to_llm(prioritize_prompt, headers, model)
    await stream_response_word_by_word(websocket, estimated_priorities, "Final Prioritization")
    
    moscow_priorities = parse_moscow_response(estimated_priorities)
    logger.info(f"MoSCoW Priorities:\n{moscow_priorities}")
    
    enriched_stories = enrich_original_stories_with_moscow(data, moscow_priorities)
    logger.info(f"Enriched Stories with MoSCoW Priorities:\n{enriched_stories}")

    return enriched_stories

# def construct_batch_moscow_prompt(stories):
#     stories_formatted = '\n'.join([
#         f"- Story ID {story['key']}: '{story['user_story']}' {story['epic']} {story['description']}"
#         for story in stories
#     ])
    
#     prompt = (
#         "You are a helpful assistant trained in MoSCoW prioritization. "
#         "For each of the following user stories, please classify them into one of the following categories based on their importance:\n"
#         "- Must Have\n"
#         "- Should Have\n"
#         "- Could Have\n"
#         "- Won't Have\n\n"
#         "Here are the stories:\n\n"
#         f"{stories_formatted}\n\n"
#         "Format the output as:\n"
#         "- Story ID X: Category"
#     )
    
#     return prompt

def construct_batch_moscow_prompt(stories, topic_response, context_response):
    stories_formatted = '\n'.join([
        f"- Story ID {story['key']}: '{story['user_story']}' (Epic: '{story['epic']}') - {story['description']}"
        for story in stories
    ])

    topic_response_direct = '\n'.join(topic_response)
    context_response_direct = '\n'.join(context_response)

    print(stories_formatted)
    print(topic_response_direct)
    print(context_response_direct)
    
    prompt = (
        "You are a helpful assistant trained in MoSCoW prioritization. "
        "For each of the following user stories, please classify them into one of the following categories based on their importance:\n"
        "- Must Have\n"
        "- Should Have\n"
        "- Could Have\n"
        "- Won't Have\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "Previously, the following points were discussed regarding prioritization:\n"
        f"{topic_response_direct}\n\n"
        "Additionally, here is the context from prior discussions:\n"
        f"{context_response_direct}\n\n"
        "Format the output as:\n"
        "- Story ID X: Category\n\n"
        "For each story, provide a detailed explanation of why it received the allocated category. What is the main reason behind its prioritization? Make sure to include a complete explanation for every story."
    )
    
    return prompt

def parse_moscow_response(response_text):
    pattern = re.compile(r"- Story ID (\d+): (Must Have|Should Have|Could Have|Won't Have)")
    moscow_priorities = []

    for match in pattern.finditer(response_text):
        story_id, category = match.groups()
        moscow_priorities.append({
            'story_id': int(story_id),
            'category': category
        })

    return moscow_priorities

def validate_moscow_response(moscow_priorities, stories):
    story_ids = {story['key'] for story in stories}
    response_story_ids = {priority['story_id'] for priority in moscow_priorities}
    
    return story_ids == response_story_ids

def enrich_original_stories_with_moscow(original_stories, moscow_priorities):
    moscow_dict = {priority['story_id']: priority['category'] for priority in moscow_priorities}

    enriched_stories = []
    for story in original_stories:
        story_id = story['key']
        story['moscow_category'] = moscow_dict.get(story_id, "No Category")
        enriched_stories.append(story)

    enriched_stories.sort(key=lambda x: ['Must Have', 'Should Have', 'Could Have', "Won't Have"].index(x['moscow_category']))
    
    return enriched_stories



# Close Moscow Technique


# KANO Functions
async def estimate_kano(data, websocket, model, topic_response, context_response):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }
    
    prioritize_prompt = construct_batch_kano_prompt(data, topic_response, context_response)
    estimated_priorities = await send_to_llm(prioritize_prompt, headers, model, )
    await stream_response_word_by_word(websocket, estimated_priorities, "Final Prioritization")
    
    kano_priorities = parse_kano_response(estimated_priorities)
    logger.info(f"KANO Priorities:\n{kano_priorities}")
    
    enriched_stories = enrich_original_stories_with_kano(data, kano_priorities)
    logger.info(f"Enriched Stories with KANO Priorities:\n{enriched_stories}")

    return enriched_stories

# def construct_batch_kano_prompt(stories):
#     stories_formatted = '\n'.join([
#         f"- Story ID {story['key']}: '{story['user_story']}' {story['epic'] {story['description']} "
#         for story in stories
#     ])
    
#     prompt = (
#         "You are a helpful assistant trained in KANO model prioritization. "
#         "For each of the following user stories, please classify them into one of the following categories based on their importance:\n"
#         "- Basic Needs\n"
#         "- Performance Needs\n"
#         "- Excitement Needs\n"
#         "- Indifferent\n"
#         "- Reverse\n\n"
#         "Here are the stories:\n\n"
#         f"{stories_formatted}\n\n"
#         "Format the output as:\n"
#         "- Story ID X: Category"
#     )
    
#     return prompt

def construct_batch_kano_prompt(stories, topic_response, context_response):
    stories_formatted = '\n'.join([
        f"- Story ID {story['key']}: '{story['user_story']}' (Epic: '{story['epic']}') - {story['description']}"
        for story in stories
    ])
    
    topic_response_direct = '\n'.join(topic_response)
    context_response_direct = '\n'.join(context_response)
    
    print(stories_formatted)
    print(topic_response_direct)
    print(context_response_direct)
    
    prompt = (
        "You are a helpful assistant trained in KANO model prioritization. "
        "For each of the following user stories, please classify them into one of the following categories based on their importance:\n"
        "- Basic Needs\n"
        "- Performance Needs\n"
        "- Excitement Needs\n"
        "- Indifferent\n"
        "- Reverse\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "Previously, the following points were discussed regarding prioritization:\n"
        f"{topic_response_direct}\n\n"
        "Additionally, here is the context from prior discussions:\n"
        f"{context_response_direct}\n\n"
        "Format the output as:\n"
        "- Story ID X: Category\n\n"
        "For each story, provide a detailed explanation of why it received the allocated category. What is the main reason behind its prioritization? Make sure to include a complete explanation for every story."
    )
    
    return prompt

def parse_kano_response(response_text):
    pattern = re.compile(r"- Story ID (\d+): (Basic Needs|Performance Needs|Excitement Needs|Indifferent|Reverse)")
    kano_priorities = []

    for match in pattern.finditer(response_text):
        story_id, category = match.groups()
        kano_priorities.append({
            'story_id': int(story_id),
            'category': category
        })

    return kano_priorities

def validate_kano_response(kano_priorities, stories):
    story_ids = {story['key'] for story in stories}
    response_story_ids = {priority['story_id'] for priority in kano_priorities}
    
    return story_ids == response_story_ids

def enrich_original_stories_with_kano(original_stories, kano_priorities):
    kano_dict = {priority['story_id']: priority['category'] for priority in kano_priorities}

    enriched_stories = []
    for story in original_stories:
        story_id = story['key']
        story['kano_category'] = kano_dict.get(story_id, "No Category")
        enriched_stories.append(story)

    enriched_stories.sort(key=lambda x: ['Basic Needs', 'Performance Needs', 'Excitement Needs', 'Indifferent', 'Reverse'].index(x['kano_category']))
    
    return enriched_stories

#close KANO TECHNIQUE


async def stream_response_word_by_word(websocket, response, agent_type, delay=0.6):

    if websocket.application_state != WebSocketState.DISCONNECTED:
        await websocket.send_json({
            "agentType": agent_type,
            "message": response
        })
        await asyncio.sleep(delay)  # Delay to simulate streaming effect  


def construct_product_owner_prompt(data, vision, mvp, rounds, first_agent_name, first_agent_prompt, client_feedback=None):
    stories_formatted = '\n'.join([
        f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    print("first_agent_prompt_is:", first_agent_prompt)

    feedback_section = ""
    if client_feedback:
        feedback_section = "As you prioritize, consider the following feedback provided by the client:\n\n" + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"

    print("Formatted Stories:")
    print(stories_formatted)
    if feedback_section:
        print("Client Feedback:")
        print(feedback_section)

    print("roundss:", rounds)

    rounds = int(rounds)

    # Generate the rounds section dynamically based on num_rounds
    rounds_section = "\n".join([f"| Round {i+1} | 0.000 |" for i in range(rounds)])
    
    # Generate the pairwise comparison section dynamically
    pairwise_section = []
    for i in range(rounds):
        for j in range(i+1, rounds):
            pairwise_section.append(f"| Round {i+1} vs Round {j+1} | 0.000 |")
    pairwise_section = "\n".join(pairwise_section)


    prompt = (
        f"You are {first_agent_name}.\n\n"
        f"{first_agent_prompt}\n\n"
        "Your task is to prioritize user stories to align with the product vision and MVP scope.\n\n"
        f"### Product Vision:\n{vision}\n\n"
        f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
        f"{feedback_section}"
        "Distribute 100 dollars (points) among the following user stories. Each dollar represents the relative importance of that story from a business and product perspective. "
        "Ensure the total equals exactly 100 dollars. Use this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "---\n"
        "### Instructions:\n"
        f"1. Perform the prioritization *{rounds} times*, revising priorities to account for changes in business goals or new insights.\n"
        "2. For each round, ensure the total adds up to 100 dollars. Use this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "### Average Kendall Tau Distance:\n"
        "Instead of showing pairwise comparisons for each round, calculate the *average Kendall Tau distance* for each round and display it in this format:\n\n"
        "| Round  | Average Kendall Tau Distance |\n"
        "|--------|-----------------------------|\n"
        f"{rounds_section}\n\n"
        "Analyze the consistency of rankings across rounds based on these values.\n\n"
        "### Pairwise Kendall Tau Distance:\n"
        "Additionally, provide the *pairwise Kendall Tau distance* between each round to understand the consistency and divergence in prioritization decisions. Present this in a table format:\n\n"
        "| Round Pair | Kendall Tau Distance |\n"
        "|------------|----------------------|\n"
        f"{pairwise_section}\n\n"
        "### Final Output:\n"
        "1. Return the *two best prioritizations* based on the average Kendall Tau analysis and alignment with business goals.\n"
        "2. For each of the two best prioritizations, ensure the total adds up to 100 dollars and present them in this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "**Prioritization 1:**\n"
        "- ID 1: X dollars\n"
        "- ID 2: Y dollars\n"
        "...\n"
        "**Prioritization 2:**\n"
        "- ID 1: A dollars\n"
        "- ID 2: B dollars\n\n"
        "3. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
        "- How the average Kendall Tau results influenced the selection.\n"
        "- Observed trends or consistencies in the rankings.\n"
        "- How these prioritizations maximize business value, address customer needs, and support overall product strategy."
    )

    return prompt


# def construct_senior_developer_prompt(data, vision, mvp, client_feedback=None):
#     stories_formatted = '\n'.join([
#         f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
#         for index, story in enumerate(data['stories'])
#     ])

#     feedback_section = ""
#     if client_feedback:
#         feedback_section = (
#             "As you prioritize, take into account the following feedback from the client:\n\n"
#             + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
#         )

#     print("Formatted Stories:")
#     print(stories_formatted)
#     if feedback_section:
#         print("Client Feedback:")
#         print(feedback_section)

#     # prompt = (
#     #     "You are a Senior Developer with extensive programming experience and a deep understanding of system architecture, technical dependencies, and best practices. "
#     #     f"{feedback_section}"
#     #     "Distribute 100 dollars (points) among the following user stories. Each dollar represents the relative importance of that story. "
#     #     "Please distribute exactly 100 dollars across these stories, ensuring the total equals exactly 100 dollars. Each dollar reflects the importance of that story from a technical perspective.\n"
#     #     "Ensure the total adds up to 100 dollars. Use this format:\n"
#     #     "- ID X: Y dollars\n"
#     #     "- ID Z: W dollars\n\n"
#     #     "Here are the stories:\n\n"
#     #     f"{stories_formatted}\n\n"
#     #     "---\n"
#     #     "### Instructions:\n"
#     #     "1. Perform the prioritization *five times*, revising priorities to account for changes in technical focus or new insights.\n"
#     #     "2. For each round, ensure the total adds up to 100 dollars. Use this format:\n"
#     #     "- ID X: Y dollars\n"
#     #     "- ID Z: W dollars\n\n"
#     #     "### Comparison:\n"
#     #     "After completing the five rounds, calculate the *Kendall Tau correlation* for all pairs of rounds (e.g., Round 1 vs. Round 2, Round 1 vs. Round 3, etc.).\n"
#     #     "Analyze the consistency of rankings across rounds based on Kendall Tau values.\n\n"
#     #     "### Final Output:\n"
#     #     "1. Return the *two best prioritizations* based on Kendall Tau analysis and technical alignment.\n"
#     #     "2. For each of the two best prioritizations, ensure the total adds up to 100 dollars and present them in this format:\n"
#     #     "- ID X: Y dollars\n"
#     #     "- ID Z: W dollars\n\n"
#     #     "3. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
#     #     "- How Kendall Tau results influenced the selection.\n"
#     #     "- Observed trends or consistencies in the rankings.\n"
#     #     "- How these prioritizations minimize technical risk and optimize system architecture, dependencies, and project flow."
#     # )
#     prompt = (
#         "You are a Senior Developer with extensive programming experience and a deep understanding of system architecture, technical dependencies, and best practices.\n\n"
#         "Your task is to prioritize user stories to align with the product vision and MVP scope.\n\n"
#         f"### Product Vision:\n{vision}\n\n"
#         f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
#         f"{feedback_section}"
#         "Distribute 100 dollars (points) among the following user stories. Each dollar represents the relative importance of that story from a technical perspective. "
#         "Ensure the total equals exactly 100 dollars. Use this format:\n"
#         "- ID X: Y dollars\n"
#         "- ID Z: W dollars\n\n"
#         "Here are the stories:\n\n"
#         f"{stories_formatted}\n\n"
#         "---\n"
#         "### Instructions:\n"
#         "1. Perform the prioritization *five times*, revising priorities to account for changes in technical focus or new insights.\n"
#         "2. For each round, ensure the total adds up to 100 dollars. Use this format:\n"
#         "- ID X: Y dollars\n"
#         "- ID Z: W dollars\n\n"
#         "### Comparison:\n"
#         "After completing the five rounds, calculate the *Kendall Tau correlation* for all pairs of rounds (e.g., Round 1 vs. Round 2, Round 1 vs. Round 3, etc.).\n"
#         "Analyze the consistency of rankings across rounds based on Kendall Tau values.\n\n"
#         "### Final Output:\n"
#         "1. Return the *two best prioritizations* based on Kendall Tau analysis and technical alignment.\n"
#         "2. For each of the two best prioritizations, ensure the total adds up to 100 dollars and present them in this format:\n"
#         "- ID X: Y dollars\n"
#         "- ID Z: W dollars\n\n"
#         "**Prioritization 1:**\n"
#         "- ID 1: X dollars\n"
#         "- ID 2: Y dollars\n"
#         "...\n"
#         "**Prioritization 2:**\n"
#         "- ID 1: A dollars\n"
#         "- ID 2: B dollars\n\n"
#         "3. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
#         "- How Kendall Tau results influenced the selection.\n"
#         "- Observed trends or consistencies in the rankings.\n"
#         "- How these prioritizations minimize technical risk and optimize system architecture, dependencies, and project flow."
#     )
#     return prompt



def construct_senior_developer_prompt(data, vision, mvp, rounds, second_agent_name, second_agent_prompt,  client_feedback=None):
    stories_formatted = '\n'.join([
        f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    feedback_section = ""
    if client_feedback:
        feedback_section = (
            "As you prioritize, take into account the following feedback from the client:\n\n"
            + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
        )

    print("Formatted Stories:")
    print(stories_formatted)
    if feedback_section:
        print("Client Feedback:")
        print(feedback_section)

    rounds = int(rounds)

    # Generate the rounds section dynamically based on num_rounds
    rounds_section = "\n".join([f"| Round {i+1} | 0.000 |" for i in range(rounds)])
    
    # Generate the pairwise comparison section dynamically
    pairwise_section = []
    for i in range(rounds):
        for j in range(i+1, rounds):
            pairwise_section.append(f"| Round {i+1} vs Round {j+1} | 0.000 |")
    pairwise_section = "\n".join(pairwise_section)

    prompt = (
        f"You are {second_agent_name}.\n\n"
        f"{second_agent_prompt}\n\n"
        "Your task is to prioritize user stories to align with the product vision and MVP scope.\n\n"
        f"### Product Vision:\n{vision}\n\n"
        f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
        f"{feedback_section}"
        "Distribute 100 dollars (points) among the following user stories. Each dollar represents the relative importance of that story from a technical perspective. "
        "Ensure the total equals exactly 100 dollars. Use this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "---\n"
        "### Instructions:\n"
        f"1. Perform the prioritization *{rounds} times*, revising priorities to account for changes in technical focus or new insights.\n"
        "2. For each round, ensure the total adds up to 100 dollars. Use this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "### Average Kendall Tau Distance:\n"
        "Instead of showing pairwise comparisons for each round, calculate the *average Kendall Tau distance* for each round and display it in this format:\n\n"
        "| Round  | Average Kendall Tau Distance |\n"
        "|--------|-----------------------------|\n"
        f"{rounds_section}\n\n"
        "Analyze the consistency of rankings across rounds based on these values.\n\n"
        "### Pairwise Kendall Tau Distance:\n"
        "Additionally, provide the *pairwise Kendall Tau distance* between each round to understand the consistency and divergence in prioritization decisions. Present this in a table format:\n\n"
        "| Round Pair | Kendall Tau Distance |\n"
        "|------------|----------------------|\n"
        f"{pairwise_section}\n\n"
        "### Final Output:\n"
        "1. Return the *two best prioritizations* based on the average Kendall Tau analysis and technical alignment.\n"
        "2. For each of the two best prioritizations, ensure the total adds up to 100 dollars and present them in this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "**Prioritization 1:**\n"
        "- ID 1: X dollars\n"
        "- ID 2: Y dollars\n"
        "...\n"
        "**Prioritization 2:**\n"
        "- ID 1: A dollars\n"
        "- ID 2: B dollars\n\n"
        "3. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
        "- How the average Kendall Tau results influenced the selection.\n"
        "- Observed trends or consistencies in the rankings.\n"
        "- How these prioritizations minimize technical risk and optimize system architecture, dependencies, and project flow."
    )

    return prompt


# def construct_solution_architect_prompt(data, vision, mvp, client_feedback=None):
#     stories_formatted = '\n'.join([
#         f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
#         for index, story in enumerate(data['stories'])
#     ])

#     feedback_section = ""
#     if client_feedback:
#         feedback_section = (
#             "As you prioritize, consider the following feedback from the client:\n\n"
#             + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
#         )

#     print("Formatted Stories:")
#     print(stories_formatted)
#     if feedback_section:
#         print("Client Feedback:")
#         print(feedback_section)

    
#     prompt = (
#         "You are an experienced Solution Architect known for designing scalable, efficient, and robust systems.\n\n"
#         "Your task is to prioritize user stories to align with the product vision and MVP scope.\n\n"
#         f"### Product Vision:\n{vision}\n\n"
#         f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
#         f"{feedback_section}"
#         "Distribute 100 dollars (points) among the following user stories. Each dollar represents the relative importance of that story from an architectural perspective. "
#         "Ensure the total adds up to exactly 100 dollars. Use this format:\n"
#         "- ID X: Y dollars\n"
#         "- ID Z: W dollars\n\n"
#         "Here are the stories:\n\n"
#         f"{stories_formatted}\n\n"
#         "---\n"
#         "### Instructions:\n"
#         "1. Perform the prioritization *five times*, revising priorities to reflect changes in architectural considerations such as scalability, performance, and integration.\n"
#         "2. For each round, ensure the total adds up to 100 dollars. Use this format:\n"
#         "- ID X: Y dollars\n"
#         "- ID Z: W dollars\n\n"
#         "### Comparison:\n"
#         "After completing the five rounds, calculate the *Kendall Tau correlation* for all pairs of rounds (e.g., Round 1 vs. Round 2, Round 1 vs. Round 3, etc.).\n"
#         "Analyze the consistency of rankings across rounds based on Kendall Tau values.\n\n"
#         "### Final Output:\n"
#         "1. Return the *two best prioritizations* based on Kendall Tau analysis and alignment with architectural goals.\n"
#         "2. For each of the two best prioritizations, ensure the total adds up to 100 dollars and present them in this format:\n"
#         "- ID X: Y dollars\n"
#         "- ID Z: W dollars\n\n"
#         "**Prioritization 1:**\n"
#         "- ID 1: X dollars\n"
#         "- ID 2: Y dollars\n"
#         "...\n"
#         "**Prioritization 2:**\n"
#         "- ID 1: A dollars\n"
#         "- ID 2: B dollars\n\n"
#         "3. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
#         "- How Kendall Tau results influenced the selection.\n"
#         "- Observed trends or consistencies in the rankings.\n"
#         "- How these prioritizations address architectural scalability, performance, and integration concerns, ensuring long-term success and alignment with strategic goals."
#     )
#     return prompt


def construct_solution_architect_prompt(data, vision, mvp, rounds, third_agent_name, third_agent_prompt, client_feedback=None):
    stories_formatted = '\n'.join([
        f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    feedback_section = ""
    if client_feedback:
        feedback_section = (
            "As you prioritize, consider the following feedback from the client:\n\n"
            + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
        )

    rounds = int(rounds)

    # Generate the rounds section dynamically based on num_rounds
    rounds_section = "\n".join([f"| Round {i+1} | 0.000 |" for i in range(rounds)])
    
    # Generate the pairwise comparison section dynamically
    pairwise_section = []
    for i in range(rounds):
        for j in range(i+1, rounds):
            pairwise_section.append(f"| Round {i+1} vs Round {j+1} | 0.000 |")
    pairwise_section = "\n".join(pairwise_section)

    prompt = (
        f"You are {third_agent_name}.\n\n"
        f"{third_agent_prompt}\n\n"
        "Your task is to prioritize user stories to align with the product vision and MVP scope.\n\n"
        f"### Product Vision:\n{vision}\n\n"
        f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
        f"{feedback_section}"
        "Distribute 100 dollars (points) among the following user stories. Each dollar represents the relative importance of that story from an architectural perspective. "
        "Ensure the total adds up to exactly 100 dollars. Use this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "---\n"
        "### Instructions:\n"
        f"1. Perform the prioritization *{rounds} times*, revising priorities to reflect changes in architectural considerations such as scalability, performance, and integration.\n"
        "2. For each round, ensure the total adds up to 100 dollars. Use this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "### Average Kendall's Tau Distance:\n"
        "After completing the rounds, calculate the *average Kendall Tau distance* for each round.\n"
        "Present the results in the following format:\n\n"
        "| Round | Average Kendall Tau Distance |\n"
        "|-------|----------------------------|\n"
        f"{rounds_section}\n\n"
         "Analyze the consistency of rankings across rounds based on these values.\n\n"
        "### Pairwise Kendall Tau Distance:\n"
        "Additionally, provide the *pairwise Kendall Tau distance* between each round to understand the consistency and divergence in prioritization decisions. Present this in a table format:\n\n"
        "| Round Pair | Kendall Tau Distance |\n"
        "|------------|----------------------|\n"
        f"{pairwise_section}\n\n"
        "### Final Output:\n"
        "1. Return the *two best prioritizations* based on average Kendall Tau analysis and alignment with architectural goals.\n"
        "2. For each of the two best prioritizations, ensure the total adds up to 100 dollars and present them in this format:\n"
        "- ID X: Y dollars\n"
        "- ID Z: W dollars\n\n"
        "**Prioritization 1:**\n"
        "- ID 1: X dollars\n"
        "- ID 2: Y dollars\n"
        "...\n"
        "**Prioritization 2:**\n"
        "- ID 1: A dollars\n"
        "- ID 2: B dollars\n\n"
        "3. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
        "- How Kendall Tau results influenced the selection.\n"
        "- Observed trends or consistencies in the rankings.\n"
        "- How these prioritizations address architectural scalability, performance, and integration concerns, ensuring long-term success and alignment with strategic goals."
    )
    return prompt
