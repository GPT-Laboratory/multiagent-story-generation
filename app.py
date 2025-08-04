
import asyncio
import base64
from datetime import datetime
import time
from io import BytesIO
import random
import logging
import os
import re
import pytz
import shutil
import textwrap
from tkinter import Image
import uuid
from bson import ObjectId
from starlette.applications import Starlette
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, JSONResponse
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from dotenv import load_dotenv
import httpx
from httpx import AsyncClient, Timeout, request
from fastapi import FastAPI, Path, UploadFile, File, Form, websockets 
from fastapi.responses import JSONResponse 
import random
import pdfplumber
from motor.motor_asyncio import AsyncIOMotorClient


from final_report import createDOCXReport, createPDFReport, get_all_reports, get_report
from final_table_prioritization import get_final_prioritization, get_final_table_prioritization
from personas import add_persona, delete_persona, get_personas, update_persona
from upgrade_user_story import upgrade_story
from wsm_helper import construct_batch_wsm_prompt_product_owner, construct_second_agent_wsm_prompt, construct_third_agent_wsm_prompt, construct_wsm_agent_1_prompt, estimate_wsm, estimate_wsm_final_Prioritization, prioritize_stories_with_wsm 
from personas import add_persona, delete_persona, get_personas, update_persona

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["MVP"]  # Database name
user_stories_collection = db["user_stories"]  # Collection name
prioritization_collection = db["prioritization_collection"]
final_table_prioritizations = db["final_table_prioritizations"]
# user_stories_collection = db["user_stories"]  

from helpers import (
    construct_product_owner_prompt, construct_senior_developer_prompt, construct_solution_architect_prompt, estimate_wsjf_final_Prioritization, extract_text_from_pdf, get_random_temperature, construct_greetings_prompt, construct_topic_prompt,
    construct_context_prompt, construct_batch_100_dollar_prompt, parse_100_dollar_response, 
    validate_dollar_distribution, enrich_agents_stories_with_dollar_distribution, enrich_stories_with_dollar_distribution,
    construct_stories_formatted, ensure_unique_keys, estimate_wsjf, estimate_moscow, 
    save_uploaded_file, parse_csv_to_json, estimate_kano, estimate_ahp, send_to_llm, send_to_llm_for_img
)
from wsjf_helper import (
    construct_wsjf_agent_1_prompt, construct_batch_wsjf_prompt_product_owner, construct_second_agent_wsjf_prompt,
    construct_third_agent_wsjf_prompt, prioritize_stories_with_wsjf
)
from table_helper import(
     get_best_stories, construct_batch_100_dollar_prompt_qa
)

from create_project import(
    convert_objectid_to_str,
    create_project,
    delete_project,
    delete_user_story,
    delete_user_story_version,
    fetch_projects,
    get_all_user_stories,
    get_user_stories,
    update_story
)

from agent_helper import (
    construct_batch_100_dollar_prompt_developer, construct_batch_100_dollar_prompt_product_owner, 
    construct_batch_100_dollar_prompt_solution_architect
)

from agent import (
    filter_stories_with_model, prioritize_stories_with_ahp, categorize_stories_with_moscow,
    generate_user_stories_with_epics,
    process_role,
    regenerate_process_role,
    parse_user_stories,
    prioritize_stories_with_100_dollar_method, OPENAI_URL, check_stories_with_framework, select_best_stories
)

LLAMA_URL="https://api.groq.com/openai/v1/chat/completions"

api_keys = [os.getenv(f"API-KEY{i}") for i in range(1, 4)]
llama_keys = [os.getenv(f"LLAMA-key{i}") for i in range(1, 3)]


print("API Keys:", api_keys)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

websocket_connections = {} 

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            request_id = data.get("request_id")
            if request_id:
                # Store the WebSocket connection with the given request_id
                websocket_connections[request_id] = websocket
                await websocket.send_json({"connection_message": f"WebSocket connected for request {request_id}"})
            if "stories" in data and "prioritization_type" in data and "model" in data:
                stories = data.get("stories")
                vision = data.get("visions")
                mvp = data.get('mvps')               
                model = data.get("model")
                client_feedback = data.get("feedback")
                rounds = data.get("rounds")
                prioritization_type = data.get("prioritization_type").upper()  # Normalize to uppercase
                 # Check if `feedback` is present to distinguish the two types of requests
                selected_panels = data.get("selected_panels", {})
                product_owner_data = selected_panels.get("productOwner")
                solution_architect_data = selected_panels.get("solutionArchitect")
                developer_data = selected_panels.get("developer")
                selected_weights = data.get("selected_weights", {})
                po_weight = selected_weights.get("po")
                sa_weight = selected_weights.get("sa")
                dev_weight = selected_weights.get("dev")
                finalPrioritization = data.get("finalPrioritization")
                agents = data.get("agents")
                project_id = data.get("project_id")
                story_id = data.get("story_id")
                print(f"prioritization-type: {prioritization_type}")
                print(f"sa_weight: {sa_weight}")
                print(f"dev_weight: {dev_weight}")
                print(f"client_feedback: {client_feedback}")
                print(f"model name-: {model}")
               
                print(f"story-id: {story_id}")

                




                if finalPrioritization is not True:
                    # Handle the original sendInput function's workflow
                    await run_agents_workflow(
                        stories,vision, mvp, prioritization_type, model, client_feedback, websocket, rounds, agents, project_id
                    )
                else:
                    # Handle the new sendInputData function's workflow
                    await handle_final_prioritization_workflow(
                        stories,
                        prioritization_type,
                        model,
                        websocket,
                        product_owner_data,
                        solution_architect_data,
                        developer_data,
                        po_weight,
                        sa_weight,
                        dev_weight,
                        rounds,
                        story_id
                    )
                # await run_agents_workflow(stories, prioritization_type, model, client_feedback, websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        if websocket.application_state != WebSocketState.DISCONNECTED:
            await websocket.close()


# client_feedback=""
async def run_agents_workflow(stories, vision, mvp, prioritization_type, model, client_feedback, websocket, rounds, agents, project_id):
   
    # Step 1: Greetings
   
    # print("Agents data:", agents)
    first_agent = agents[0]
    second_agent = agents[1]
    third_agent = agents[2]
    first_agent_name = first_agent.get("role")
    first_agent_prompt = first_agent.get("prioritization")
    first_agent_role = first_agent.get("name")


    second_agent_name = second_agent.get("role")
    second_agent_prompt = second_agent.get("prioritization")
    second_agent_role = second_agent.get("name")


    third_agent_name = third_agent.get("role")
    third_agent_prompt = third_agent.get("prioritization")
    third_agent_role = third_agent.get("name")

    print("stories", stories)

    # return


    if prioritization_type == "100_DOLLAR":

        greetings_prompt = construct_product_owner_prompt({"stories": stories}, vision, mvp, rounds, first_agent_name, first_agent_prompt, client_feedback )
        # greetings_response = await engage_agents(greetings_prompt, websocket, "PO", model)
        greetings_response = await engage_agents(greetings_prompt, websocket, first_agent_role, model, project_id, prioritization_type)
        # Debug: Print what we're sending to frontend
        print("Sending to frontend:", {
            "agentType": "Best product owner stories", 
            "message": greetings_response
        })
        # Step 2: Topic Introduction
        topic_prompt = construct_senior_developer_prompt({"stories": stories}, vision, mvp, rounds, second_agent_name, second_agent_prompt, client_feedback )    #logger.info(f"topic_prompt : {topic_prompt}")
        
        # Step 3: Context and Discussion
        context_prompt = construct_solution_architect_prompt({"stories": stories}, vision, mvp, rounds, third_agent_name, third_agent_prompt, client_feedback ) 
        
        # Run Step 2 and Step 3 concurrently
        topic_response, context_response = await asyncio.gather(
            engage_agents(topic_prompt, websocket, second_agent_role, model, project_id, prioritization_type),
            engage_agents(context_prompt, websocket, third_agent_role, model, project_id, prioritization_type)
        )

        PO_rounds = construct_batch_100_dollar_prompt_product_owner({"stories": stories}, greetings_response )
        print("po rounds", PO_rounds)
        
        best_PO_rounds = await engage_all_agents_in_prioritization(PO_rounds, stories, websocket, model, prioritization_type)
        await websocket.send_json({
                "agentType": "Best product owner rounds", 
                # "message": best_rounds,
                "message": {
            "round_one": best_PO_rounds[0],
            "round_two": best_PO_rounds[1],
        }
        })

        SA_rounds = construct_batch_100_dollar_prompt_solution_architect({"stories": stories}, topic_response )
        best_SA_rounds = await engage_all_agents_in_prioritization(SA_rounds, stories, websocket, model, prioritization_type)
        await websocket.send_json({
                "agentType": "Best solution architect rounds", 
                # "message": best_rounds,
                "message": {
            "round_one": best_SA_rounds[0],
            "round_two": best_SA_rounds[1]
        }
        })

        developer_rounds = construct_batch_100_dollar_prompt_developer({"stories": stories}, context_response )
        best_developer_rounds = await engage_all_agents_in_prioritization(developer_rounds, stories, websocket, model, prioritization_type)
        await websocket.send_json({
                "agentType": "Best developer rounds", 
                # "message": best_rounds,
                "message": {
            "round_one": best_developer_rounds[0],
            "round_two": best_developer_rounds[1]
        }
        })

    elif prioritization_type == "WSJF":
        print("WSJF working")
        agent_1_prompt =  construct_wsjf_agent_1_prompt({"stories": stories}, vision, mvp, rounds, first_agent_name, first_agent_prompt, client_feedback)
        wsjf_greetings_response = await engage_agents(agent_1_prompt, websocket, first_agent_name, model ,  project_id, prioritization_type)
        # Debug: Print what we're sending to frontend
        print("Sending to frontend:", {
            "agentType": "Best product owner stories", 
            "message": wsjf_greetings_response
        })
        agent_1_rounds = construct_batch_wsjf_prompt_product_owner({"stories": stories}, wsjf_greetings_response )
        best_agent_1_rounds = await estimate_wsjf(agent_1_rounds, stories, websocket, model, prioritization_type)
        await websocket.send_json({
                "agentType": "Best product owner rounds", 
                # "message": best_rounds,
                "message": {
            "round_one": best_agent_1_rounds[0],
            "round_two": best_agent_1_rounds[1]
        }
        })
        
        # 2nd and 3rd agent consequent rounds
        agent_2_prompt =  construct_second_agent_wsjf_prompt({"stories": stories}, vision, mvp, rounds, second_agent_name, second_agent_prompt, client_feedback=None)
        agent_3_prompt =  construct_third_agent_wsjf_prompt({"stories": stories}, vision, mvp, rounds, second_agent_name, second_agent_prompt, client_feedback=None)
        # Run Step 2 and Step 3 concurrently
        topic_response_agent_2, context_response_agent_3 = await asyncio.gather(
            engage_agents(agent_2_prompt, websocket, second_agent_name, model,project_id, prioritization_type),
            engage_agents(agent_3_prompt, websocket, third_agent_name, model,project_id, prioritization_type)
        )
        
        # 2nd Agent Progress
        agent_2_rounds = construct_batch_wsjf_prompt_product_owner({"stories": stories}, topic_response_agent_2 )
        best_agent_2_rounds = await estimate_wsjf(agent_2_rounds, stories, websocket, model, prioritization_type)
        await websocket.send_json({
                "agentType": "Best solution architect rounds", 
                # "message": best_rounds,
                "message": {
            "round_one": best_agent_2_rounds[0],
            "round_two": best_agent_2_rounds[1]
        }
        })

        # 3rd Agent Progress
        agent_3_rounds = construct_batch_wsjf_prompt_product_owner({"stories": stories}, context_response_agent_3 )
        best_agent_3_rounds = await estimate_wsjf(agent_3_rounds, stories, websocket, model, prioritization_type)
        await websocket.send_json({
                "agentType": "Best developer rounds", 
                # "message": best_rounds,
                "message": {
            "round_one": best_agent_3_rounds[0],
            "round_two": best_agent_3_rounds[1]
        }
        })
    elif prioritization_type == "WSM":
        print("WSM working")
        criteria = {
            "Business Value": (0.30, "The potential value the feature provides to the business."),
            "Technical Feasibility": (0.25, "How easy or difficult is the feature to implement?"),
            "Strategic Alignment": (0.20, "Does this feature align with the company's strategic goals?"),
            "Risk & Compliance": (0.15, "Does the feature address regulatory or security concerns?"),
            "Scalability": (0.10, "How well does the feature scale with business growth?")
        }

        agent_1_prompt =  construct_wsm_agent_1_prompt({"stories": stories}, vision, mvp, rounds, first_agent_name, first_agent_prompt, client_feedback)
        wsm_greetings_response = await engage_agents(agent_1_prompt, websocket, first_agent_name, model,project_id, prioritization_type)
        # Debug: Print what we're sending to frontend
        print("Sending to frontend:", {
            "agentType": "Best product owner stories", 
            "message": wsm_greetings_response
        })
        agent_1_rounds = construct_batch_wsm_prompt_product_owner({"stories": stories}, wsm_greetings_response )
        best_agent_1_rounds = await estimate_wsm(agent_1_rounds, stories, websocket, model, prioritization_type)
        await websocket.send_json({
                "agentType": "Best product owner rounds", 
                # "message": best_rounds,
                "message": {
            "round_one": best_agent_1_rounds[0],
            "round_two": best_agent_1_rounds[1]
        }
        })
        
        # 2nd and 3rd agent consequent rounds
        agent_2_prompt =  construct_second_agent_wsm_prompt({"stories": stories}, vision, mvp, rounds, second_agent_name, second_agent_prompt, client_feedback=None)
        agent_3_prompt =  construct_third_agent_wsm_prompt({"stories": stories}, vision, mvp, rounds, second_agent_name, second_agent_prompt, client_feedback=None)
        # Run Step 2 and Step 3 concurrently
        topic_response_agent_2, context_response_agent_3 = await asyncio.gather(
            engage_agents(agent_2_prompt, websocket, second_agent_name, model,project_id, prioritization_type),
            engage_agents(agent_3_prompt, websocket, third_agent_name, model,project_id, prioritization_type)
        )
        
        # 2nd Agent Progress
        agent_2_rounds = construct_batch_wsm_prompt_product_owner({"stories": stories}, topic_response_agent_2 )
        best_agent_2_rounds = await estimate_wsm(agent_2_rounds, stories, websocket, model, prioritization_type)
        await websocket.send_json({
                "agentType": "Best solution architect rounds", 
                # "message": best_rounds,
                "message": {
            "round_one": best_agent_2_rounds[0],
            "round_two": best_agent_2_rounds[1]
        }
        })

        # 3rd Agent Progress
        agent_3_rounds = construct_batch_wsm_prompt_product_owner({"stories": stories}, context_response_agent_3 )
        best_agent_3_rounds = await estimate_wsm(agent_3_rounds, stories, websocket, model, prioritization_type)
        await websocket.send_json({
                "agentType": "Best developer rounds", 
                # "message": best_rounds,
                "message": {
            "round_one": best_agent_3_rounds[0],
            "round_two": best_agent_3_rounds[1]
        }
        })

async def engage_agents(prompt, websocket, agent_type, model, project_id, prioritization_type, max_retries=1):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

    agent_prompt = {"role": "user", "content": prompt}
    
    logger.info(f"Engaging agents with prompt: {prompt}")
    agent_response = await send_to_llm(agent_prompt['content'], headers, model, prioritization_type)
    
    if agent_response:
        await stream_response_word_by_word(websocket, agent_response, agent_type, project_id, prioritization_type)
    else:
        agent_response = "No response from agent"
    
    return agent_response


async def engage_all_agents_in_prioritization(prompt, stories, websocket, model, prioritization_type, max_retries=2 ):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

    logger.info(f"Engaging agents in prioritization with prompt: {prompt}")
    for attempt in range(max_retries):
        try:
            final_response = await send_to_llm(prompt, headers, model, prioritization_type)
            logger.info(f"Final response from agent: {final_response}")  # Detailed logging
            # await stream_response_word_by_word(websocket, final_response, "Final Prioritization")

            dollar_distribution = parse_100_dollar_response(final_response)

            if not dollar_distribution:
                logger.error(f"Failed to parse dollar distribution: {final_response}")
                continue

            logger.info(f"Dollar Response: {dollar_distribution}")
            
            enriched_stories = enrich_agents_stories_with_dollar_distribution(stories, dollar_distribution)
            # await websocket.send_json({"agentType": "Final Prioritization", "message": {"stories": enriched_stories}})
            return enriched_stories

        except Exception as e:
            logger.error(f"Error during prioritization attempt {attempt + 1}: {str(e)}")
        logger.info(f"Retrying prioritization... ({attempt + 1}/{max_retries})")

    raise Exception("Failed to get valid response from agents after multiple attempts")


async def prioritize_stories_with_weightage(stories, product_owner_data, solution_architect_data, developer_data, po_weight, sa_weight, dev_weight):
    # Format the input data for OpenAI API
    formatted_product_owner_data = '\n'.join([f"- {story}" for story in product_owner_data])
    formatted_solution_architect_data = '\n'.join([f"- {story}" for story in solution_architect_data])
    formatted_developer_data = '\n'.join([f"- {story}" for story in developer_data])

    prompt = (
    "You are an expert at prioritizing tasks. Your goal is to distribute 100 dollars across user stories to reflect their priority. "
    "The prioritization is based on input from three roles:\n"
    f"- Product Owner {po_weight}%: Focused on business and client needs.\n"
    f"- Solution Architect {sa_weight}%: Focused on technical feasibility and architecture.\n"
    f"- Developer {dev_weight}%: Focused on implementation complexity and development aspects.\n\n"
    "Here are the user stories:\n"
    + '\n'.join([f"- Story ID {index + 1}: {story['user_story']} {story['epic']} {story['description']}" for index, story in enumerate(stories)])
    + "\n\n"
    "Each role has provided their input:\n\n"
    f"Product Owner's perspective {po_weight}%:\n{formatted_product_owner_data}\n\n"
    f"Solution Architect's input {sa_weight}%:\n{formatted_solution_architect_data}\n\n"
    f"Developer's feedback {dev_weight}%:\n{formatted_developer_data}\n\n"
    "Distribute 100 dollars across all stories based on the input, adhering strictly to the following weights:\n"
    f"- Product Owner: {po_weight}% influence\n"
    f"- Solution Architect: {sa_weight}% influence\n"
    f"- Developer: {dev_weight}% influence\n\n"
    "Focus more on the Product Owner's perspective while proportionally considering the inputs of the Solution Architect and Developer. "
    "Ensure the sum of all dollar allocations equals exactly 100.\n\n"
    "Strictly Return the prioritized stories in this format:\n"
    "- Story ID X: dollars Y\n"
    "- Story ID Z: dollars W\n\n"
    "The number of prioritized stories and the total dollar allocation must match the number of input stories and 100 dollars, respectively."
)

    return prompt
    # # Parse the response (ensure the output is well-structured and matches the input story count)
    # prioritized_stories = response.splitlines()
    # return prioritized_stories



async def engage_agents_in_prioritization(prompt, stories, websocket, model,prioritization_type, story_id, max_retries=1 ):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

    logger.info(f"Engaging agents in prioritization with prompt: {prompt}")
    for attempt in range(max_retries):
        try:
            final_response = await send_to_llm(prompt, headers, model, prioritization_type )
            logger.info(f"Final response from agent: {final_response}")  # Detailed logging
            await stream_response_word_by_word(websocket, final_response,    "Final Prioritization", story_id, prioritization_type)

            dollar_distribution = parse_100_dollar_response(final_response)

            if not dollar_distribution:
                logger.error(f"Failed to parse dollar distribution: {final_response}")
                continue

            logger.info(f"Dollar Response: {dollar_distribution}")
            
            enriched_stories = enrich_stories_with_dollar_distribution(stories, dollar_distribution)
            # print("final comes",enriched_stories)
            # await websocket.send_json({"agentType": "Final Prioritization", "message": {"stories": enriched_stories}})
            # If the agent type is "Final Prioritization", insert into MongoDB
            final_prioritization_table = { 
                "agentType": "Final_output_into_table",
                "prioritization_type": prioritization_type,
                "story_id": story_id,
                "message": enriched_stories
            }

            # Insert into MongoDB collection
            final_table_prioritizations.insert_one(final_prioritization_table) 

            return enriched_stories

        except Exception as e:
            logger.error(f"Error during prioritization attempt {attempt + 1}: {str(e)}")
        logger.info(f"Retrying prioritization... ({attempt + 1}/{max_retries})")

    raise Exception("Failed to get valid response from agents after multiple attempts")



async def handle_final_prioritization_workflow(
    stories, prioritization_type, model, websocket, product_owner_data, solution_architect_data, developer_data, po_weight, sa_weight, dev_weight, round, story_id
):
    
    if prioritization_type == "100_DOLLAR":
        # Step 4: Prioritization
        prioritize_weight_prompt = await prioritize_stories_with_weightage(
            stories, product_owner_data, solution_architect_data, developer_data, po_weight, sa_weight, dev_weight
        )

        prioritized_stories = await engage_agents_in_prioritization(prioritize_weight_prompt, stories, websocket, model, prioritization_type, story_id)
    elif prioritization_type == "WSJF":
        prioritize_weight_prompt = await prioritize_stories_with_wsjf(
            stories, product_owner_data, solution_architect_data, developer_data, po_weight, sa_weight, dev_weight
        )

        print("Prioritize Weight Prompt:", prioritize_weight_prompt)
        prioritized_stories = await estimate_wsjf_final_Prioritization(prioritize_weight_prompt, stories, websocket, model, prioritization_type)
    elif prioritization_type == "WSM":
        prioritize_weight_prompt = await prioritize_stories_with_wsm(
            stories, product_owner_data, solution_architect_data, developer_data, po_weight, sa_weight, dev_weight
        )

        prioritized_stories = await estimate_wsm_final_Prioritization(prioritize_weight_prompt, stories, websocket, model, prioritization_type)

    # Step 6: Final Output in table
    await asyncio.sleep(1)  # Delay of 1 second between greetings
    await websocket.send_json({"agentType": "Final_output_into_table", "message": prioritized_stories, "prioritization_type": prioritization_type})

    # Stream the result to the client
    # await stream_response_word_by_word(websocket, "Here is the final prioritized output:", "Final Prioritization")
    # await asyncio.sleep(1)  # Delay of 1 second
    # await websocket.send_json({
    #     "agentType": "Final_output_into_table",
    #     "message": prioritized_stories,
    #     "prioritization_type": prioritization_type,
    # })



async def stream_response_word_by_word(websocket, response, agent_type, story_id, prioritization_type, delay=0.6):
    
    if websocket.application_state != WebSocketState.DISCONNECTED:
        await websocket.send_json({
            "agentType": agent_type,
            "message": response
        })

        # If the agent type is "Final Prioritization", insert into MongoDB
        if agent_type == "Final Prioritization":
            final_prioritization = { 
                "agentType": agent_type,
                "prioritization_type": prioritization_type,
                "story_id": story_id,
                "message": response
            }

            # Insert into MongoDB collection
            prioritization_collection.insert_one(final_prioritization)  
            # print(f"Inserted final_prioritization record with ID: {inserted_doc.inserted_id}")
            return

async def stream_response_as_complete_message(websocket: WebSocket, response: str, agent_type: str, delay: float = 0.6):
    if websocket.application_state != WebSocketState.DISCONNECTED:
        await websocket.send_json({
            "agentType": agent_type,
            "message": response
        })
        await asyncio.sleep(delay)  # Delay to simulate streaming effect            

async def catch_all(request):
    return FileResponse(os.path.join('dist', 'index.html'))


async def generate_user_stories(request: Request):
    start_time = time.perf_counter()
    data = await request.json()
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

    if not data or 'vision' not in data or 'model' not in data:
        return JSONResponse({'error': 'Missing required data: vision, and model'}, status_code=400)

    model = data['model']
    vision = data['vision']
    mvp = data['mvp']
    user_analysis = data['user_analysis']
    feedback = data['feedback']
    request_id = data.get("request_id")
    context_image = data.get("context_image")
    agents = data.get("agents")
    new_version = data.get("new_version")  # Default to False if not provided

    roles = [agent["role"] for agent in agents]
    project_id = data.get("project_id")
    selected_user_story = data.get("selectedUserStory")

    print(f"selected user story: {selected_user_story}")

    print(f"feedback: {feedback}")
    print(f"project ID: {project_id}")

    image_data = None
    if context_image:
        image_data = base64.b64decode(context_image)

    websocket = websocket_connections.get(request_id)

    if not websocket:
        print(f"No WebSocket connection found for request_id: {request_id}")
    else:
        print(f"WebSocket connection found for request_id: {request_id}")

    input_content = {
        "vision": vision,
        "mvp": mvp,
        "user_analysis": user_analysis,
        "previous_response": None
    }

    # Run process_role for all roles in parallel
    tasks = [process_role(input_content, context_image, model, headers, role, feedback) for role in roles]
    responses = await asyncio.gather(*tasks)  # Wait for all responses

    print("Generated responses:", responses)

    best_stories = filter_stories_with_model(responses, model, headers)

    # Parse the final selected stories
    final_response = parse_user_stories(best_stories)
    utc_time = datetime.utcnow()

    # Assign a unique ObjectId to each story
    for story in final_response:
        story["_id"] = ObjectId()
        story["created_at"] = str(utc_time)

    end_time = time.perf_counter()  # End timing
    response_time = end_time - start_time  # in seconds

    if selected_user_story:
        existing_entry = await user_stories_collection.find_one({"_id": ObjectId(selected_user_story)})
        if existing_entry:
            if new_version:
                # Insert new entry with selected_user_story
                await user_stories_collection.insert_one({
                    "project_id": project_id,
                    "vision": vision,
                    "mvp": mvp,
                    "user_analysis": user_analysis,
                    "agents": agents,
                    "model": model,
                    "stories": final_response,
                    "response_time": response_time,
                    "created_at": str(utc_time)  # Store in UTC

                })
            else:
                # Append to the existing stories array
                await user_stories_collection.update_one(
                    {"_id": ObjectId(selected_user_story)},
                    {"$push": {"stories": {"$each": final_response}}}
                )
        else:
            # If no existing entry, insert a new one
            await user_stories_collection.insert_one({
                "project_id": project_id,
                "vision": vision,
                "mvp": mvp,
             "user_analysis": user_analysis,
                "agents": agents,
                "model": model,
                "stories": final_response,
                "response_time": response_time,
                "created_at": str(utc_time)  # Store in UTC
            })
    else:
        # If selected_user_story is undefined, insert a new entry
        await user_stories_collection.insert_one({
            "project_id": project_id,
            "vision": vision,
            "mvp": mvp,
            "user_analysis": user_analysis,
            "agents": agents,
            "model": model,
            "stories": final_response,
            "response_time": response_time,
            "created_at": str(utc_time)  # Store in UTC
            
        })


    return JSONResponse({
        "message": "User stories generated and stored successfully",
        "final_response": convert_objectid_to_str(final_response),
        "response_time": response_time

    })


async def regenerate_user_stories(request: Request):
    data = await request.json()
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

    if not data or 'model' not in data:
        return JSONResponse({'error': 'Missing required data: vision, and model'}, status_code=400)

    model = data['model']
    generated_stories = data['generated_stories']
    feedback = data['feedback']
    request_id = data.get("request_id")
    project_id = data.get("project_id")
    vision = data.get("vision")
    mvp = data.get("mvp")
    user_analysis = data.get("user_analysis")
    agents = data.get("agents")
    selected_user_story = data.get("selectedUserStory")

    # agents = data.get("agents")

    # roles = [agent["role"] for agent in agents]

    print(f"feedback: {feedback}")

    # Define the roles in sequence

    # Initial input to the first role (PO) is based on the original data
    input_content = {
        "generated_stories": generated_stories,
        "previous_response": None  # No previous response for the first model
    }

    websocket = websocket_connections.get(request_id)

    if not websocket:
        print(f"No WebSocket connection found for request_id: {request_id}")
    else:
        print(f"WebSocket connection found for request_id: {request_id}")
    
        
    response = regenerate_process_role(input_content, model, headers, feedback)

    # Parse the final response (from Compliance)
    final_response = parse_user_stories(response)

    for story in final_response:
        story["_id"] = ObjectId()

    try:
        object_id = ObjectId(selected_user_story)
        existing_entry = await user_stories_collection.find_one({"_id": object_id})

        if existing_entry:
            await user_stories_collection.delete_one({"_id": object_id})
            
        await user_stories_collection.insert_one({
            "_id": object_id,
            "project_id": project_id,
            "vision": vision,
            "mvp": mvp,
            "user_analysis": user_analysis,
            "agents": agents,
            "model": model,
            "stories": final_response
        })

    except Exception as e:
        return JSONResponse({"error": "Invalid ObjectId or database operation failed", "details": str(e)}, status_code=400)

    return JSONResponse({
        "message": "User stories regenerated and stored successfully",
        "final_response": convert_objectid_to_str(final_response)
    })


async def check_user_stories_quality(request: Request):
    data = await request.json()
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }
    if not data or 'framework' not in data or 'stories' not in data or 'model' not in data:
        return JSONResponse({'error': 'Missing required data: framework, stories, and model'}, status_code=400)
    
    model = data['model']
    framework = data['framework']
    stories = data['stories']
    stories_with_epics = check_stories_with_framework(framework, stories, model, headers)
    return JSONResponse({"stories_with_epics": stories_with_epics})


async def generate_user_stories_by_files(request: Request):
    # Define UPLOAD_FOLDER before using it
    current_dir = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    form = await request.form()
    vision_file = form.get("vision_file")
    mvp_file = form.get("mvp_file")
    model = form.get("model")
    feedback = form.get("feedback")

    if not vision_file or not mvp_file or not model:
        return JSONResponse({'error': 'Missing required data: vision_file, mvp_file, and model'}, status_code=400)

    # Save the vision file
    vision_file_path, vision_file_error = save_uploaded_file(UPLOAD_FOLDER, vision_file)
    if vision_file_error:
        return JSONResponse({'error': vision_file_error}, status_code=400)
    
    # Save the MVP file
    mvp_file_path, mvp_file_error = save_uploaded_file(UPLOAD_FOLDER, mvp_file)
    if mvp_file_error:
        return JSONResponse({'error': mvp_file_error}, status_code=400)
    
    # Extract text from the vision and MVP files
    try:
        def extract_text_from_pdf(file_path):
            with pdfplumber.open(file_path) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        vision_text = extract_text_from_pdf(vision_file_path)
        mvp_text = extract_text_from_pdf(mvp_file_path)

    except Exception as e:
        return JSONResponse({'error': f"Error extracting text from files: {str(e)}"}, status_code=400)

    # Combine the extracted texts
    combined_text = f"Vision Document:\n{vision_text}\n\nMVP Document:\n{mvp_text}"

    # Generate user stories using the combined text
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

    try:
        stories_with_epics = generate_user_stories_with_epics(vision_text, mvp_text, "", model, headers)
    except Exception as e:
        return JSONResponse({'error': f"Error generating user stories: {str(e)}"}, status_code=500)

    # If feedback exists and mentions the response is bad, regenerate
    if feedback and "bad" in feedback.lower():
        # Logic to regenerate the response (for simplicity, here just re-call the function)
        stories_with_epics = generate_user_stories_with_epics(vision_text, mvp_text, "", model, headers)

    return JSONResponse({"stories_with_epics": stories_with_epics})


# local_tz = pytz.timezone('Asia/Karachi')
async def upload_csv(request: Request):
    form = await request.form()
    file = form.get("file")
    project_id = form.get("project_id")

   

    if not file:
        return JSONResponse({'error': 'No file part'}, status_code=400)
    
    file_path, error = save_uploaded_file(UPLOAD_FOLDER, file)
    
    if error:
        return JSONResponse({'error': error}, status_code=400)
    if file_path:
        csv_data = parse_csv_to_json(file_path)
        print(csv_data)
        print(project_id)

        # Check if any story lacks _id and assign ObjectId
        for story in csv_data:
            if "_id" not in story:
                story["_id"] = ObjectId()
                # story["_id"] = str(ObjectId())

        await user_stories_collection.insert_one({
            "project_id": project_id,
            "vision": "",
            "mvp": "",
            "user_analysis": "",
            "agents": "",
            "model": "",
            "stories": csv_data,
            "created_at": str(datetime.utcnow())
        })


    return JSONResponse({"stories_with_epics": convert_objectid_to_str(csv_data)})

current_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Starlette(debug=True, middleware=[
    Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
], routes=[
    Route("/api/create-project", create_project, methods=["POST"]),
    Route('/api/generate-user-stories', generate_user_stories, methods=['POST']),
    Route('/api/regenerate-user-stories', regenerate_user_stories, methods=['POST']),
    Route('/api/generate-user-stories-by-files', generate_user_stories_by_files, methods=['POST']),
    Route('/api/upload-csv', upload_csv, methods=['POST']),
    Route('/api/check-user-stories-quality', check_user_stories_quality, methods=['POST']),
    Route('/api/personas/{project_id}', get_personas, methods=['GET']),
    Route('/api/user_stories/{project_id}', get_user_stories, methods=['GET']),
    Route('/api/user_stories', get_all_user_stories, methods=['GET']),

    Route("/api/add-personas", add_persona, methods=["POST"]),
    Route("/api/delete-persona/{persona_id}", delete_persona, methods=["DELETE"]),
    Route("/api/update-persona/{persona_id}", update_persona, methods=["PUT"]),
    Route("/api/projects", fetch_projects, methods=["GET"]),
    Route("/api/delete-project/{project_id}", delete_project, methods=["DELETE"]),
    Route("/api/upgrade_story", upgrade_story, methods=["POST"]),
    Route("/api/update_story", update_story, methods=["PUT"]),
    Route("/api/delete-user-story/{story_id}", delete_user_story, methods=["DELETE"]),
    Route("/api/delete-user-story-version/{story_id}", delete_user_story_version, methods=["DELETE"]),
    Route('/api/create-project-report-docx', createDOCXReport, methods=['POST']),
    Route('/api/create-project-report-pdf', createPDFReport, methods=['POST']),
    Route("/api/get-all-reports/{selectedUserStoryId}", get_all_reports, methods=["GET"]),
    Route("/api/get-report/{file_id}", get_report, methods=["GET"]),
    Route("/api/get-final-table-prioritization/{story_id}", get_final_table_prioritization, methods=["GET"]),
    Route("/api/get-final-prioritization/{story_id}", get_final_prioritization, methods=["GET"]),




    
    WebSocketRoute("/api/ws-chat", websocket_endpoint),
    Mount('/', StaticFiles(directory='dist', html=True), name='static')
])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0', port=8000)