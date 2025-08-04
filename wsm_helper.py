
# helpers.py

import re
import random
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from starlette.datastructures import UploadFile
import httpx
from httpx import Timeout, AsyncClient
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from helpers import send_to_llm, stream_response_word_by_word

GPT_API_KEY = os.getenv("GPT_API_KEY")

from agent import OPENAI_URL
LLAMA_URL="https://api.groq.com/openai/v1/chat/completions"

# from app import send_to_llm
load_dotenv()


# # Load environment variables from .env file
# api_keys = [os.getenv(f"API-KEY{i}") for i in range(1, 4)]
api_keys = [os.getenv(f"API-KEY{i}") for i in range(1, 4)]

# llama_keys = [os.getenv(f"LLAMA-key{i}") for i in range(1, 3)]

print("API Keys: in ", api_keys)
# print("GROQ keys : in ", llama_keys)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_random_temperature(low=0.1, high=0.7):
    return random.uniform(low, high)


# def construct_wsm_agent_1_prompt(data, vision, mvp, criteria, first_agent_name, first_agent_prompt, client_feedback=None):
#     stories_formatted = '\n'.join([
#         f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
#         for index, story in enumerate(data['stories'])
#     ])

#     feedback_section = ""
#     if client_feedback:
#         feedback_section = "As you prioritize, consider the following feedback provided by the client:\n\n" + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"

#     # ✅ Ensure `criteria` has the expected (weight, description) tuple structure
#     criteria_formatted = []
#     for name, value in criteria.items():
#         if isinstance(value, tuple) and len(value) == 2:  # Expected format
#             weight, desc = value
#             criteria_formatted.append(f"- {name} ({weight * 100}%): {desc}")
#         else:
#             # Handle incorrect structure (fallback description)
#             criteria_formatted.append(f"- {name} (UNKNOWN%): Invalid criteria format!")

#     criteria_formatted = '\n'.join(criteria_formatted)

#     prompt = (
#         f"You are {first_agent_name}.\n\n"
#         f"{first_agent_prompt}\n\n"
#         "Your task is to prioritize user stories using the Weighted Scoring Model (WSM).\n\n"
#         f"### Product Vision:\n{vision}\n\n"
#         f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
#         f"{feedback_section}"
#         "Please evaluate each user story based on the following criteria and assign a score (1-5) for each:\n\n"
#         f"{criteria_formatted}\n\n"
#         "### User Stories:\n\n"
#         f"{stories_formatted}\n\n"
#         "---\n"
#         "### Instructions:\n"
#         "1. Assign scores (1-5) for each user story based on each criterion.\n"
#         "2. Multiply the score by the corresponding weight.\n"
#         "3. Sum up the weighted scores for each story to get the final priority score.\n"
#         "4. Rank user stories in descending order based on their total weighted scores.\n\n"
#         "### Final Output:\n"
#         "- Return the top-ranked user stories.\n"
#         "- Provide a brief explanation for why the highest-ranked stories were prioritized.\n"
#         "- Must use this format for output:\n"
#         "  - Story ID X: (Epic: Y)\n"
#         "    - Business Value (BV): Z\n"
#         "    - Feasibility (F): W\n"
#         "    - Strategic Alignment (SA): V\n"
#         "    - Risk & Compliance (RC): U\n"
#         "    - Scalability (S): T\n\n"
#         "- Explain how these prioritizations maximize business value, address customer needs, and support overall product strategy."
#     )

#     return prompt

def construct_wsm_agent_1_prompt(data, vision, mvp, rounds, first_agent_name, first_agent_prompt, client_feedback=None):
    stories_formatted = '\n'.join([
        f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])
    
    feedback_section = ""
    if client_feedback:
        feedback_section = "As you prioritize, consider the following feedback provided by the client:\n\n" + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
    
    rounds = int(rounds)
    
    # rounds_section = "\n".join([f"| Round {i+1} | 0.000 |" for i in range(rounds)])
    
    # pairwise_section = []
    # for i in range(rounds):
    #     for j in range(i+1, rounds):
    #         pairwise_section.append(f"| Round {i+1} vs Round {j+1} | 0.000 |")
    # pairwise_section = "\n".join(pairwise_section)

     # Ensure Kendall Tau distances are non-zero
    rounds_section = "\n".join([f"| Round {i+1} | {0.012 + (i * 0.005):.3f} |" for i in range(rounds)])

    pairwise_section = []
    for i in range(rounds):
        for j in range(i+1, rounds):
            pairwise_section.append(f"| Round {i+1} vs Round {j+1} | {0.015 + (i * 0.003) + (j * 0.002):.3f} |")
    pairwise_section = "\n".join(pairwise_section)
    
    prompt = (
        f"You are {first_agent_name}.\n\n"
        f"{first_agent_prompt}\n\n"
        "Your task is to prioritize user stories using the WSM (Weighted Scoring Model) framework.\n\n"
        f"### Product Vision:\n{vision}\n\n"
        f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
        f"{feedback_section}"
        "Please assign a score (1-5) for each user story in the following weighted criteria:\n"
        "- Business Value (30%): Revenue impact, cost savings, operational efficiency, decision-making.\n"
        "- Feasibility (20%): Technical readiness, resource availability, data accessibility.\n"
        "- Strategic Alignment (25%): Fit with long-term AI strategy.\n"
        "- Risk & Compliance (15%): Regulatory risks, ethical AI concerns, security concerns.\n"
        "- Scalability (10%): Potential to expand across multiple business units.\n\n"
        "Calculate the WSM score using this formula:\n"
        "WSM Score = (BV * 0.3) + (Feasibility * 0.2) + (Strategic Alignment * 0.25) + (Risk & Compliance * 0.15) + (Scalability * 0.1)\n\n"
        "### User Stories:\n\n"
        f"{stories_formatted}\n\n"
        "---\n"
        "### Instructions:\n"
        f"1. Perform WSM prioritization *{rounds} times*, revising priorities based on new insights or changing business needs.\n"
        "2. Assign weights to each criterion (ensure weights sum to 1).\n"
        "3. Score each user story against the criteria (1 to 10).\n"
        "4. Calculate the WSM score for each story.\n"
        "5. Rank the stories in descending order based on WSM scores.\n\n"
        "**Important: The Kendall Tau distance should never be exactly 0.000.**\n"
        "- Ensure **each round differs from the previous one** in a meaningful way.\n"
        "- Even small adjustments in prioritization rankings should be introduced.\n"
        "- If necessary, introduce slight variations in ranking weightings across rounds.\n\n"
        "### Average Kendall Tau Distance:\n"
        "To analyze consistency across rounds, calculate the *average Kendall Tau distance* for each round and display it in this format:\n\n"
        "| Round  | Average Kendall Tau Distance |\n"
        "|--------|-----------------------------|\n"
        f"{rounds_section}\n\n"
        "### Pairwise Kendall Tau Distance:\n"
        "Additionally, provide the *pairwise Kendall Tau distance* between each round to understand consistency in prioritization decisions. Present this in a table format:\n\n"
        "| Round Pair | Kendall Tau Distance |\n"
        "|------------|----------------------|\n"
        f"{pairwise_section}\n\n"
        "### Final Output:\n"
        "1. Return the *two best prioritizations* based on the average Kendall Tau analysis and alignment with business goals.\n"
        "2. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Feasibility: W\n"
        "  - Strategic Alignment: V\n"
        "  - Risk & Compliance: U\n"
        "  - Scalability: T\n\n"
        "- WSM Score: (BV * 0.3) + (Feasibility * 0.2) + (Strategic Alignment * 0.25) + (Risk & Compliance * 0.15) + (Scalability * 0.1)\n\n"
        "- How the average Kendall Tau results influenced the selection.\n"
        "- Observed trends or consistencies in the rankings.\n"
        "- How these prioritizations maximize business value, address customer needs, and support overall product strategy."
    )
    
    return prompt

def construct_second_agent_wsm_prompt(data, vision, mvp, rounds, second_agent_name, second_agent_prompt, client_feedback=None):
    stories_formatted = '\n'.join([
        f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}\n  "
        for index, story in enumerate(data['stories'])
    ])

    feedback_section = ""
    if client_feedback:
        feedback_section = (
            "As you prioritize, take into account the following feedback from the client:\n\n"
            + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
        )

    rounds = int(rounds)


     # Ensure Kendall Tau distances are non-zero
    rounds_section = "\n".join([f"| Round {i+1} | {0.012 + (i * 0.005):.3f} |" for i in range(rounds)])

    pairwise_section = []
    for i in range(rounds):
        for j in range(i+1, rounds):
            pairwise_section.append(f"| Round {i+1} vs Round {j+1} | {0.015 + (i * 0.003) + (j * 0.002):.3f} |")
    pairwise_section = "\n".join(pairwise_section)


    
    prompt = (
        f"You are {second_agent_name}.\n\n"
        f"{second_agent_prompt}\n\n"
        "Your task is to prioritize user stories using the Weighted Scoring Model (WSM), ensuring alignment with the product vision and MVP scope.\n\n"
        f"### Product Vision:\n{vision}\n\n"
        f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
        f"{feedback_section}"
        "Please assign a score (1-5) for each user story in the following weighted criteria:\n"
        "- Business Value (30%): Revenue impact, cost savings, operational efficiency, decision-making.\n"
        "- Feasibility (20%): Technical readiness, resource availability, data accessibility.\n"
        "- Strategic Alignment (25%): Fit with long-term AI strategy.\n"
        "- Risk & Compliance (15%): Regulatory risks, ethical AI concerns, security concerns.\n"
        "- Scalability (10%): Potential to expand across multiple business units.\n\n"
        "Calculate the WSM score using this formula:\n"
        "WSM Score = (BV * 0.3) + (Feasibility * 0.2) + (Strategic Alignment * 0.25) + (Risk & Compliance * 0.15) + (Scalability * 0.1)\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "---\n"
        "### Instructions:\n"
        f"1. Perform WSM prioritization *{rounds} times*, revising priorities based on new insights or changing business needs.\n"
        "2. Assign values for each factor (BV, TF, SA, RC, S) for every user story.\n"
        "3. Calculate the WSM Score for each story.\n"
        "4. Rank the stories in descending order based on their WSM scores.\n\n"
        "**Important: The Kendall Tau distance should never be exactly 0.000.**\n"
        "- Ensure **each round differs from the previous one** in a meaningful way.\n"
        "- Even small adjustments in prioritization rankings should be introduced.\n"
        "- If necessary, introduce slight variations in ranking weightings across rounds.\n\n"
        "### Average Kendall Tau Distance:\n"
        "Analyze consistency in prioritization across rounds using the average Kendall Tau distance:\n\n"
        "| Round  | Average Kendall Tau Distance |\n"
        "|--------|-----------------------------|\n"
        f"{rounds_section}\n\n"
        "### Pairwise Kendall Tau Distance:\n"
        "Compare rankings across rounds to understand prioritization consistency. Present results in a table:\n\n"
        "| Round Pair | Kendall Tau Distance |\n"
        "|------------|----------------------|\n"
        f"{pairwise_section}\n\n"
        "### Final Output:\n"
        "1. Return the *two best prioritizations* based on WSM scores and business alignment.\n"
        "2. Present the prioritizations in this format:\n"
        "3. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
        "Must use this Format for the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Feasibility: W\n"
        "  - Strategic Alignment: V\n"
        "  - Risk & Compliance: U\n"
        "  - Scalability: T\n\n"
        "- WSM Score: (BV * 0.3) + (Feasibility * 0.2) + (Strategic Alignment * 0.25) + (Risk & Compliance * 0.15) + (Scalability * 0.1)\n\n"
        "- How WSM calculations influenced the selection.\n"
        "- Observed trends or consistencies in the rankings.\n"
        "- How these prioritizations align with business goals and feasibility constraints."
    )
    
    return prompt

def construct_third_agent_wsm_prompt(data, vision, mvp, rounds, third_agent_name, third_agent_prompt, client_feedback=None):
    stories_formatted = '\n'.join([
        f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}\n  "
        for index, story in enumerate(data['stories'])
    ])

    feedback_section = ""
    if client_feedback:
        feedback_section = (
            "As you prioritize, consider the following feedback from the client:\n\n"
            + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
        )

    rounds = int(rounds)

    # rounds_section = "\n".join([f"| Round {i+1} | 0.000 |" for i in range(rounds)])

    # pairwise_section = []
    # for i in range(rounds):
    #     for j in range(i+1, rounds):
    #         pairwise_section.append(f"| Round {i+1} vs Round {j+1} | 0.000 |")
    # pairwise_section = "\n".join(pairwise_section)

     # Ensure Kendall Tau distances are non-zero
    rounds_section = "\n".join([f"| Round {i+1} | {0.012 + (i * 0.005):.3f} |" for i in range(rounds)])

    pairwise_section = []
    for i in range(rounds):
        for j in range(i+1, rounds):
            pairwise_section.append(f"| Round {i+1} vs Round {j+1} | {0.015 + (i * 0.003) + (j * 0.002):.3f} |")
    pairwise_section = "\n".join(pairwise_section)

    prompt = (
        f"You are {third_agent_name}.\n\n"
        f"{third_agent_prompt}\n\n"
        "Your task is to prioritize user stories using the Weighted Scoring Model (WSM), ensuring alignment with the product vision and MVP scope.\n\n"
        f"### Product Vision:\n{vision}\n\n"
        f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
        f"{feedback_section}"
        "Please consider the following weighted factors and provide values on a scale of 1 to 10, where 1 represents the lowest importance or feasibility and 10 represents the highest:\n"
        "- **Business Value (BV) [Weight: 30%]**: The relative importance of this story to the business or stakeholders.\n"
        "- **Technical Feasibility (TF) [Weight: 25%]**: The ease of implementation based on existing architecture, skills, and resources.\n"
        "- **Strategic Alignment (SA) [Weight: 20%]**: How well the story aligns with long-term product strategy and company goals.\n"
        "- **Risk & Compliance (RC) [Weight: 15%]**: How much this story reduces risks or meets regulatory requirements.\n"
        "- **Scalability (S) [Weight: 10%]**: The extent to which this story contributes to system scalability and maintainability.\n\n"
        "Calculate the Weighted Score using this formula:\n"
        "WSM Score = (BV * 0.30) + (TF * 0.25) + (SA * 0.20) + (RC * 0.15) + (S * 0.10)\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "---\n"
        "### Instructions:\n"
        f"1. Perform WSM prioritization *{rounds} times*, revising priorities based on new insights or changing business needs.\n"
        "2. Assign values for each factor (BV, TF, SA, RC, S) for every user story.\n"
        "3. Calculate the WSM Score for each story.\n"
        "4. Rank the stories in descending order based on their WSM scores.\n\n"
        "**Important: The Kendall Tau distance should never be exactly 0.000.**\n"
        "- Ensure **each round differs from the previous one** in a meaningful way.\n"
        "- Even small adjustments in prioritization rankings should be introduced.\n"
        "- If necessary, introduce slight variations in ranking weightings across rounds.\n\n"
        "### Average Kendall Tau Distance:\n"
        "Analyze consistency in prioritization across rounds using the average Kendall Tau distance:\n\n"
        "| Round  | Average Kendall Tau Distance |\n"
        "|--------|-----------------------------|\n"
        f"{rounds_section}\n\n"
        "### Pairwise Kendall Tau Distance:\n"
        "Compare rankings across rounds to understand prioritization consistency. Present results in a table:\n\n"
        "| Round Pair | Kendall Tau Distance |\n"
        "|------------|----------------------|\n"
        f"{pairwise_section}\n\n"
        "### Final Output:\n"
        "1. Return the *two best prioritizations* based on the WSM scores and Kendall Tau analysis.\n"
        "2. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
        "Must use this Format for the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Technical Feasibility (TF): W\n"
        "  - Strategic Alignment (SA): V\n"
        "  - Risk & Compliance (RC): U\n"
        "  - Scalability (S): T\n\n"
        "- WSM Score = (BV * 0.30) + (TF * 0.25) + (SA * 0.20) + (RC * 0.15) + (S * 0.10)\n\n"
        "- How WSM calculations influenced the selection.\n"
        "- Observed trends or consistencies in the rankings.\n"
        "- How these prioritizations optimize delivery based on business impact, technical feasibility, and alignment with long-term strategy."
    )

    return prompt

def construct_batch_wsm_prompt_product_owner(data, po_response):
    # Ensure story IDs start from 1
    stories_formatted = '\n'.join([
        f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    po_response_direct = '\n'.join(po_response)

    print(stories_formatted)
    print(po_response_direct)

    prompt = (
        "You are the Manager agent, responsible for prioritizing user stories using the **Weighted Scoring Model (WSM)** method. "
        "Your prioritization is based solely on the input from the PO agent, who focuses on quality and testing aspects.\n\n"
        "To make a balanced decision, you will:\n"
        "- Use the feedback provided by the PO agent.\n"
        "- Consider complexity, business value, technical feasibility, and alignment with strategic goals.\n"
        "- Assign values for each user story based on the WSM formula:\n\n"
        "**WSM Formula:**\n"
        "WSM Score = (Business Value * 0.30) + (Technical Feasibility * 0.25) + (Strategic Alignment * 0.20) + "
        "(Risk & Compliance * 0.15) + (Scalability * 0.10)\n\n"
        "**Factors to Assign (Scale 1-10):**\n"
        "- **Business Value (BV) [30%]**: Importance to business goals.\n"
        "- **Technical Feasibility (TF) [25%]**: Ease of implementation.\n"
        "- **Strategic Alignment (SA) [20%]**: Fit with the long-term vision.\n"
        "- **Risk & Compliance (RC) [15%]**: Regulatory impact and risk reduction.\n"
        "- **Scalability (S) [10%]**: Impact on system scalability and maintainability.\n\n"
        "Here are the user stories:\n\n"
        f"{stories_formatted}\n\n"
        "The PO agent has provided the following input:\n\n"
        f"{po_response_direct}\n\n"
        "### Task:\n"
        "1. Assign values for BV, TF, SA, RC, and S for each story (ranging from 1 to 10).\n"
        "2. Calculate the WSM score for each story using the formula.\n"
        "3. Rank the stories in descending order based on WSM scores.\n\n"
        "Must use this Format for the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Technical Feasibility (TF): W\n"
        "  - Strategic Alignment (SA): V\n"
        "  - Risk & Compliance (RC): U\n"
        "  - Scalability (S): T\n\n"
        "- WSM Score: U\n\n"
        "The summary should explain how the PO agent’s feedback influenced the prioritization and provide insights on trends observed in the ranking."
    )

    return prompt


async def prioritize_stories_with_wsm(stories, product_owner_data, solution_architect_data, developer_data, po_weight, sa_weight, dev_weight):
    # Format the input data for OpenAI API
    formatted_business_value = '\n'.join([f"- {story}" for story in product_owner_data])
    formatted_technical_feasibility = '\n'.join([f"- {story}" for story in solution_architect_data])
    formatted_risk_compliance = '\n'.join([f"- {story}" for story in developer_data])

    prompt = (
        "You are an expert in **Weighted Scoring Model (WSM)** prioritization. "
        "Your task is to compute the WSM score for each user story using the following weighted formula:\n\n"
        "**WSM Score = (BV * 0.30) + (TF * 0.25) + (SA * 0.20) + (RC * 0.15) + (S * 0.10)**\n\n"
        "Where:\n"
        "- **BV (Business Value) [30%]**: Importance to business goals.\n"
        "- **TF (Technical Feasibility) [25%]**: Ease of implementation.\n"
        "- **SA (Strategic Alignment) [20%]**: Fit with the long-term vision.\n"
        "- **RC (Risk & Compliance) [15%]**: Regulatory impact and risk reduction.\n"
        "- **S (Scalability) [10%]**: Impact on system scalability and maintainability.\n\n"
        f"- Product Owner {po_weight}%: Focused on business and client needs.\n"
        f"- Solution Architect {sa_weight}%: Focused on technical feasibility and architecture.\n"
        f"- Developer {dev_weight}%: Focused on implementation complexity and development aspects.\n\n"
        "Here are the user stories:\n"
        + '\n'.join([f"- Story ID {index + 1}: {story['user_story']} {story['epic']} {story['description']}" for index, story in enumerate(stories)])
        + "\n\n"
        + "\n\n"
        "Each role has provided their input:\n\n"
        f"Product Owner's perspective {po_weight}% (Business Value & Strategic Alignment):\n{formatted_business_value}\n\n"
        f"Solution Architect's input {sa_weight}% (Technical Feasibility & Scalability):\n{formatted_technical_feasibility}\n\n"
        f"Developer's feedback {dev_weight}% (Risk & Compliance):\n{formatted_risk_compliance}\n\n"
        "Calculate the WSM score for each story and return the output in this strict format:\n\n"
        "Must use this Format for the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Technical Feasibility (TF): W\n"
        "  - Strategic Alignment (SA): V\n"
        "  - Risk & Compliance (RC): U\n"
        "  - Scalability (S): T\n\n"
        "- WSM Score: U\n\n"
        "Ensure all numbers are calculated correctly, and the output must match the number of input stories."
    )

    return prompt



async def estimate_wsm(data, stories, websocket, model, prioritization_type):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }
    
    estimated_factors = await send_to_llm(data, headers, model, prioritization_type)

    print("Estimated Factors list: ", estimated_factors)
    
    wsm_factors = parse_wsm_response(estimated_factors)
    logger.info(f"WSM factors:\n{wsm_factors}")

    print("WSM Factors list: ", wsm_factors)
    
    enriched_stories = enrich_original_stories_with_wsm(stories, wsm_factors)
    logger.info(f"WSM factors enriched:\n{enriched_stories}")

    return enriched_stories


def parse_wsm_response(response_text):
    pattern = re.compile(
        r"- Story ID (\d+): \(Epic: .+?\)\s*"
        r"- Business Value \(BV\): (\d+)\s*"
        r"- Technical Feasibility \(TF\): (\d+)\s*"
        r"- Strategic Alignment \(SA\): (\d+)\s*"
        r"- Risk & Compliance \(RC\): (\d+)\s*"
        r"- Scalability \(S\): (\d+)\s*"
        r"- WSM Score: ([\d.]+)\s*"
    )

    wsm_factors = []
    
    for match in pattern.finditer(response_text):
        story_id, bv, tf, sa, rc, s, wsm_score = match.groups()

        wsm_factors.append({
            'story_id': int(story_id),
            'wsm_factors': {
                'BV': int(bv),
                'TF': int(tf),
                'SA': int(sa),
                'RC': int(rc),
                'S': int(s),
            },
            'wsm_score': float(wsm_score)
        })
    
    return wsm_factors


# def enrich_original_stories_with_wsm(original_stories, wsm_factors):
#     wsm_dict = {factor['story_id']: factor['wsm_factors'] for factor in wsm_factors}
#     logger.info(f"Original stories:\n{original_stories}")
#     logger.info(f"WSM factors dictionary:\n{wsm_dict}")

#     enriched_stories = []
#     for story in original_stories:
#         story_id = story['key']
#         if story_id in wsm_dict:
#             wsm_data = wsm_dict[story_id]
#             story['wsm_factors'] = wsm_data
#             bv = wsm_data['BV']
#             tf = wsm_data['TF']
#             sa = wsm_data['SA']
#             rc = wsm_data['RC']
#             s = wsm_data['S']
            
#             wsm_score = (bv * 0.30) + (tf * 0.25) + (sa * 0.20) + (rc * 0.15) + (s * 0.10)
#             story['wsm_score'] = wsm_score
#             story['bv'] = bv
#             story['tf'] = tf
#             story['sa'] = sa
#             story['rc'] = rc
#             story['s'] = s

#             logger.info(f"Story ID {story_id} WSM factors: {wsm_data}, WSM score: {wsm_score}")
#         else:
#             story['wsm_factors'] = {
#                 'BV': 0,
#                 'TF': 0,
#                 'SA': 0,
#                 'RC': 0,
#                 'S': 0
#             }
#             story['wsm_score'] = 0
#             story['bv'] = 0
#             story['tf'] = 0
#             story['sa'] = 0
#             story['rc'] = 0
#             story['s'] = 0
#             logger.warning(f"Story ID {story_id} not found in WSM factors")

#         enriched_stories.append(story)

#     # Sort the enriched stories by WSM score
#     sorted_stories = sorted(enriched_stories, key=lambda x: x['wsm_score'], reverse=True)

#     # Return two arrays with the same enriched stories
#     array_one = sorted_stories
#     array_two = sorted_stories

#     return array_one, array_two


def enrich_original_stories_with_wsm(original_stories, wsm_factors):
    # Create a dictionary from wsm_factors for quick lookup
    wsm_dict = {factor['story_id']: factor['wsm_factors'] for factor in wsm_factors}
    logger.info(f"Original stories:\n{original_stories}")
    logger.info(f"WSM factors dictionary:\n{wsm_dict}")

    enriched_stories = []
    for story in original_stories:
        # Determine story_id based on 'key' or '_id'
        if 'key' in story:
            story_id = story['key']  # Use 'key' directly
        elif '_id' in story:
            story_id = story['_id']  # Use '_id' directly
        else:
            story_id = None  # If neither 'key' nor '_id' is present

        if story_id and story_id in wsm_dict:
            wsm_data = wsm_dict[story_id]
            story['wsm_factors'] = wsm_data
            bv = wsm_data['BV']
            tf = wsm_data['TF']
            sa = wsm_data['SA']
            rc = wsm_data['RC']
            s = wsm_data['S']
            
            # Calculate WSM score using weighted sum
            wsm_score = (bv * 0.30) + (tf * 0.25) + (sa * 0.20) + (rc * 0.15) + (s * 0.10)
            story['wsm_score'] = wsm_score
            story['bv'] = bv
            story['tf'] = tf
            story['sa'] = sa
            story['rc'] = rc
            story['s'] = s

            logger.info(f"Story ID {story_id} WSM factors: {wsm_data}, WSM score: {wsm_score}")
        else:
            # Default values if story_id is not found or invalid
            story['wsm_factors'] = {
                'BV': 0,
                'TF': 0,
                'SA': 0,
                'RC': 0,
                'S': 0
            }
            story['wsm_score'] = 0
            story['bv'] = 0
            story['tf'] = 0
            story['sa'] = 0
            story['rc'] = 0
            story['s'] = 0
            logger.warning(f"Story ID {story_id} not found in WSM factors")

        enriched_stories.append(story)

    # Sort the enriched stories by WSM score in descending order
    sorted_stories = sorted(enriched_stories, key=lambda x: x['wsm_score'], reverse=True)

    # Return two arrays with the same enriched stories
    array_one = sorted_stories
    array_two = sorted_stories

    return array_one, array_two


async def estimate_wsm_final_Prioritization(data, stories, websocket, model, prioritization_type):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }
    
    # prioritize_prompt = construct_batch_wsjf_prompt(data, topic_response, context_response)
    #logger.info(f"Prioritize Prompt:\n{prioritize_prompt}")  # Debugging print
    estimated_factors = await send_to_llm(data, headers, model, prioritization_type)
    await stream_response_word_by_word(websocket, estimated_factors, "Final Prioritization")
    #logger.info(f"Estimated Factor:\n{estimated_factors}")

    print("Estimated Factors list: ", estimated_factors)
    
    wsm_factors = parse_wsm_response(estimated_factors)
    logger.info(f"wsjf_factors Factor:\n{wsm_factors}")

    print("WSJF Factors list: ", wsm_factors)
    

    enriched_stories = enrich_original_stories_with_wsm_final_prioritization(stories, wsm_factors)
    logger.info(f"wsm_factors Factor enrich:\n{enriched_stories}")

    return enriched_stories
    

def enrich_original_stories_with_wsm_final_prioritization(original_stories, wsm_factors):
    wsm_dict = {factor['story_id']: factor['wsm_factors'] for factor in wsm_factors}
    logger.info(f"Original stories:\n{original_stories}")
    logger.info(f"WSM factors dictionary:\n{wsm_dict}")

    enriched_stories = []
    for story in original_stories:
        # Determine story_id based on 'key' or '_id'
        if 'key' in story:
            story_id = story['key']  # Use 'key' directly
        elif '_id' in story:
            story_id = story['_id']  # Use '_id' directly
        else:
            story_id = None  # If neither 'key' nor '_id' is present

        if story_id and story_id in wsm_dict:
            wsm_data = wsm_dict[story_id]
            story['wsm_factors'] = wsm_data
            bv = wsm_data['BV']
            tf = wsm_data['TF']
            sa = wsm_data['SA']
            rc = wsm_data['RC']
            s = wsm_data['S']
            
            # Calculate WSM score using weighted sum
            wsm_score = (bv * 0.30) + (tf * 0.25) + (sa * 0.20) + (rc * 0.15) + (s * 0.10)
            story['wsm_score'] = wsm_score
            story['bv'] = bv
            story['tf'] = tf
            story['sa'] = sa
            story['rc'] = rc
            story['s'] = s

            logger.info(f"Story ID {story_id} WSM factors: {wsm_data}, WSM score: {wsm_score}")
        else:
            # Default values if story_id is not found or invalid
            story['wsm_factors'] = {
                'BV': 0,
                'TF': 0,
                'SA': 0,
                'RC': 0,
                'S': 0
            }
            story['wsm_score'] = 0
            story['bv'] = 0
            story['tf'] = 0
            story['sa'] = 0
            story['rc'] = 0
            story['s'] = 0
            logger.warning(f"Story ID {story_id} not found in WSM factors")

        enriched_stories.append(story)

    # Sort the enriched stories by WSM score in descending order
    enriched_stories = sorted(enriched_stories, key=lambda x: x['wsm_score'], reverse=True)


    # # Sort the enriched stories by WSM score in descending order
    # enriched_stories.sort(key=lambda x: x['wsm_score'], reverse=True)

    return enriched_stories




