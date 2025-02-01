import asyncio
import base64
from io import BytesIO
import random
import logging
import os
import re
import shutil
import textwrap
from tkinter import Image
import uuid
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

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

from helpers import (
    construct_product_owner_prompt, construct_senior_developer_prompt, construct_solution_architect_prompt, extract_text_from_pdf, get_random_temperature, construct_greetings_prompt, construct_topic_prompt,
    construct_context_prompt, construct_batch_100_dollar_prompt, parse_100_dollar_response, 
    validate_dollar_distribution, enrich_agents_stories_with_dollar_distribution, enrich_stories_with_dollar_distribution,
    construct_stories_formatted, ensure_unique_keys, estimate_wsjf, estimate_moscow, 
    save_uploaded_file, parse_csv_to_json, estimate_kano, estimate_ahp, send_to_llm, send_to_llm_for_img
)

from table_helper import(
     get_best_stories, construct_batch_100_dollar_prompt_qa
)

from agent_helper import (
    construct_batch_100_dollar_prompt_developer, construct_batch_100_dollar_prompt_product_owner, 
    construct_batch_100_dollar_prompt_solution_architect
)

from agent import (
    prioritize_stories_with_ahp, categorize_stories_with_moscow,
    generate_user_stories_with_epics,
    process_role,
    regenerate_process_role,
    parse_user_stories,
    prioritize_stories_with_100_dollar_method, OPENAI_URL, check_stories_with_framework
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
                print(f"po_weight: {po_weight}")
                print(f"sa_weight: {sa_weight}")
                print(f"dev_weight: {dev_weight}")
                print(f"client_feedback: {client_feedback}")

                if finalPrioritization is not True:
                    # Handle the original sendInput function's workflow
                    await run_agents_workflow(
                        stories,vision, mvp, prioritization_type, model, client_feedback, websocket, rounds
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
                        rounds
                    )
                # await run_agents_workflow(stories, prioritization_type, model, client_feedback, websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        if websocket.application_state != WebSocketState.DISCONNECTED:
            await websocket.close()


# client_feedback=""
async def run_agents_workflow(stories, vision, mvp, prioritization_type, model, client_feedback, websocket, rounds):
   
    # Step 1: Greetings
    greetings_prompt = construct_product_owner_prompt({"stories": stories}, vision, mvp, rounds, client_feedback )


    greetings_response = await engage_agents(greetings_prompt, websocket, "PO", model)

    PO_rounds = construct_batch_100_dollar_prompt_product_owner({"stories": stories}, greetings_response )
    
    best_PO_rounds = await engage_all_agents_in_prioritization(PO_rounds, stories, websocket, model)

    await websocket.send_json({
            "agentType": "Best product owner rounds", 
            # "message": best_rounds,
            "message": {
        "round_one": best_PO_rounds[0],
        "round_two": best_PO_rounds[1]
    }
    })


    
    # Debug: Print what we're sending to frontend
    print("Sending to frontend:", {
        "agentType": "Best product owner stories", 
        "message": greetings_response
    })
    
    # await websocket.send_json({
    #     "agentType": "Best product owner stories", 
    #     "message": greetings_response
    # })

    try:
        # Log the raw response for debugging
        logger.info(f"Raw greetings response: {greetings_response}")

        # # Improved parsing logic
        # greetings = greetings_response.split("2. ")
        # pekka_greeting = greetings[0].strip()
        # remaining_greetings = greetings[1].split("3. ")
        # sami_greeting = remaining_greetings[0].strip()
        # zeeshan_greeting = remaining_greetings[1].strip()

        # Send greetings with delay
        # stream_response_word_by_word(websocket, greetings_response, "PO")
        #await asyncio.sleep(1)  # Delay of 1 second between greetings
        
        #await stream_response_word_by_word(websocket, sami_greeting, "QA")
        #await asyncio.sleep(1)  # Delay of 1 second between greetings
        
        #await stream_response_word_by_word(websocket, zeeshan_greeting, "developer")
    except Exception as e:
        logger.error(f"Error parsing greetings response: {greetings_response}")
        logger.error(f"Exception: {e}")
        #await websocket.send_json({"agentType": "error", "message": "Error parsing greetings response. Please try again later."})

     # Step 2: Topic Introduction
    topic_prompt = construct_senior_developer_prompt({"stories": stories}, vision, mvp, rounds, client_feedback )    #logger.info(f"topic_prompt : {topic_prompt}")
    
    # Step 3: Context and Discussion
    context_prompt = construct_solution_architect_prompt({"stories": stories}, vision, mvp, rounds, client_feedback ) 
    
    # Run Step 2 and Step 3 concurrently
    topic_response, context_response = await asyncio.gather(
        engage_agents(topic_prompt, websocket, "Solution Architect", model),
        engage_agents(context_prompt, websocket, "developer", model)
    )

    SA_rounds = construct_batch_100_dollar_prompt_solution_architect({"stories": stories}, topic_response )
    
    best_SA_rounds = await engage_all_agents_in_prioritization(SA_rounds, stories, websocket, model)

    await websocket.send_json({
            "agentType": "Best solution architect rounds", 
            # "message": best_rounds,
            "message": {
        "round_one": best_SA_rounds[0],
        "round_two": best_SA_rounds[1]
    }
    })
    developer_rounds = construct_batch_100_dollar_prompt_developer({"stories": stories}, context_response )
    
    best_developer_rounds = await engage_all_agents_in_prioritization(developer_rounds, stories, websocket, model)

    await websocket.send_json({
            "agentType": "Best developer rounds", 
            # "message": best_rounds,
            "message": {
        "round_one": best_developer_rounds[0],
        "round_two": best_developer_rounds[1]
    }
    })
    # Send QA and Developer best stories
    # if qa_best_stories:
    #     await websocket.send_json({
    #         "agentType": "Best solution architect stories", 
    #         "message": qa_best_stories
    #     })
    
    # if dev_best_stories:
    #     await websocket.send_json({
    #         "agentType": "Best developer stories", 
    #         "message": dev_best_stories
    #     })

    #logger.info(f"topic_prompt response: {topic_response}")
    
    # Step 4: Prioritization
    # if prioritization_type == "100_DOLLAR":
    #     # prioritize_prompt = construct_batch_100_dollar_prompt({"stories": stories}, topic_response, context_response)
    #     prioritize_prompt = construct_batch_100_dollar_prompt({"stories": stories}, topic_response, context_response, greetings_response )
       
    #     prioritized_stories = await engage_agents_in_prioritization(prioritize_prompt, stories, websocket, model)
    #     print("Final 100 dollar", prioritized_stories)
    # elif prioritization_type == "WSJF":
    #     prioritized_stories = await estimate_wsjf(stories, websocket, model, topic_response, context_response)
    # elif prioritization_type == "MOSCOW":
    #     prioritized_stories = await estimate_moscow(stories, websocket, model, topic_response, context_response)
    # elif prioritization_type == "KANO":
    #     prioritized_stories = await estimate_kano(stories, websocket, model, topic_response, context_response)
    # elif prioritization_type == "AHP":
    #     prioritized_stories = await estimate_ahp({"stories": stories}, websocket, model, topic_response, context_response)    
    # else:
    #     raise ValueError(f"Unsupported prioritization type: {prioritization_type}")

    # # Step 5: Final Output
    # await stream_response_word_by_word(websocket, "Here is the final prioritized output:", "Final Prioritization")

    # # Step 6: Final Output in table
    # await asyncio.sleep(1)  # Delay of 1 second between greetings
    # await websocket.send_json({"agentType": "Final_output_into_table", "message": prioritized_stories, "prioritization_type": prioritization_type})


async def engage_agents(prompt, websocket, agent_type, model, max_retries=1):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

    agent_prompt = {"role": "user", "content": prompt}
    
    logger.info(f"Engaging agents with prompt: {prompt}")
    agent_response = await send_to_llm(agent_prompt['content'], headers, model)
    
    if agent_response:
        await stream_response_word_by_word(websocket, agent_response, agent_type)
    else:
        agent_response = "No response from agent"
    
    return agent_response


async def engage_all_agents_in_prioritization(prompt, stories, websocket, model, max_retries=2 ):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

    logger.info(f"Engaging agents in prioritization with prompt: {prompt}")
    for attempt in range(max_retries):
        try:
            final_response = await send_to_llm(prompt, headers, model)
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
    "Return the prioritized stories in this format:\n"
    "- Story ID X: dollars Y\n"
    "- Story ID Z: dollars W\n\n"
    "The number of prioritized stories and the total dollar allocation must match the number of input stories and 100 dollars, respectively."
)

    return prompt
    # # Parse the response (ensure the output is well-structured and matches the input story count)
    # prioritized_stories = response.splitlines()
    # return prioritized_stories



async def engage_agents_in_prioritization(prompt, stories, websocket, model, max_retries=1 ):
    headers = {
        "Authorization": f"Bearer {random.choice(api_keys)}",
        "Content-Type": "application/json"
    }

    logger.info(f"Engaging agents in prioritization with prompt: {prompt}")
    for attempt in range(max_retries):
        try:
            final_response = await send_to_llm(prompt, headers, model)
            logger.info(f"Final response from agent: {final_response}")  # Detailed logging
            await stream_response_word_by_word(websocket, final_response, "Final Prioritization")

            dollar_distribution = parse_100_dollar_response(final_response)

            if not dollar_distribution:
                logger.error(f"Failed to parse dollar distribution: {final_response}")
                continue

            logger.info(f"Dollar Response: {dollar_distribution}")
            
            enriched_stories = enrich_stories_with_dollar_distribution(stories, dollar_distribution)
            # await websocket.send_json({"agentType": "Final Prioritization", "message": {"stories": enriched_stories}})
            return enriched_stories

        except Exception as e:
            logger.error(f"Error during prioritization attempt {attempt + 1}: {str(e)}")
        logger.info(f"Retrying prioritization... ({attempt + 1}/{max_retries})")

    raise Exception("Failed to get valid response from agents after multiple attempts")



# async def handle_final_prioritization_workflow(stories,
#                         prioritization_type,
#                         model,
#                         websocket,
#                         product_owner_data,
#                         solution_architect_data,
#                         developer_data,):
#     # Step 4: Prioritization
#     if prioritization_type == "100_DOLLAR":
#         # prioritize_prompt = construct_batch_100_dollar_prompt({"stories": stories}, product_owner_data, solution_architect_data)
#         prioritize_prompt = construct_batch_100_dollar_prompt({"stories": stories}, product_owner_data, solution_architect_data, developer_data )
       
#         prioritized_stories = await engage_agents_in_prioritization(prioritize_prompt, stories, websocket, model)
#         print("Final 100 dollar", prioritized_stories)
#     elif prioritization_type == "WSJF":
#         prioritized_stories = await estimate_wsjf(stories, websocket, model, product_owner_data, solution_architect_data)
#     elif prioritization_type == "MOSCOW":
#         prioritized_stories = await estimate_moscow(stories, websocket, model, product_owner_data, solution_architect_data)
#     elif prioritization_type == "KANO":
#         prioritized_stories = await estimate_kano(stories, websocket, model, product_owner_data, solution_architect_data)
#     elif prioritization_type == "AHP":
#         prioritized_stories = await estimate_ahp({"stories": stories}, websocket, model, product_owner_data, solution_architect_data)    
#     else:
#         raise ValueError(f"Unsupported prioritization type: {prioritization_type}")

#     # Step 5: Final Output
#     await stream_response_word_by_word(websocket, "Here is the final prioritized output:", "Final Prioritization")

#     # Step 6: Final Output in table
#     await asyncio.sleep(1)  # Delay of 1 second between greetings
#     await websocket.send_json({"agentType": "Final_output_into_table", "message": prioritized_stories, "prioritization_type": prioritization_type})

async def handle_final_prioritization_workflow(
    stories, prioritization_type, model, websocket, product_owner_data, solution_architect_data, developer_data, po_weight, sa_weight, dev_weight
):
    # Weighted prioritization
    prioritize_weight_prompt = await prioritize_stories_with_weightage(
        stories, product_owner_data, solution_architect_data, developer_data, po_weight, sa_weight, dev_weight
    )

    prioritized_stories = await engage_agents_in_prioritization(prioritize_weight_prompt, stories, websocket, model)  # Assuming `engage_agents_in_prioritization` interacts with OpenAI API
    
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



async def stream_response_word_by_word(websocket, response, agent_type, delay=0.6):
    
    if websocket.application_state != WebSocketState.DISCONNECTED:
        await websocket.send_json({
            "agentType": agent_type,
            "message": response
        })
        # await asyncio.sleep(delay)  # Delay to simulate streaming effect  

async def stream_response_as_complete_message(websocket: WebSocket, response: str, agent_type: str, delay: float = 0.6):
    if websocket.application_state != WebSocketState.DISCONNECTED:
        await websocket.send_json({
            "agentType": agent_type,
            "message": response
        })
        await asyncio.sleep(delay)  # Delay to simulate streaming effect            

async def catch_all(request):
    return FileResponse(os.path.join('dist', 'index.html'))





# async def generate_user_stories(request: Request):
#     data = await request.json()
#     headers = {
#         "Authorization": f"Bearer {random.choice(api_keys)}",
#         "Content-Type": "application/json"
#     }

#     if not data or 'vision' not in data or 'model' not in data:
#         return JSONResponse({'error': 'Missing required data: vision, and model'}, status_code=400)

#     model = data['model']
#     vision = data['vision']
#     mvp = data['mvp']
#     glossary = data['glossary']
#     user_analysis = data['user_analysis']
#     feedback = data['feedback']
#     request_id = data.get("request_id")

#     print(f"feedback: {feedback}")

#     # Define the roles in sequence
#     roles = ["PO", "SA", "Security", "Compliance"]

#     # Initial input to the first role (PO) is based on the original data
#     input_content = {
#         "vision": vision,
#         "mvp": mvp,
#         "glossary": glossary,
#         "user_analysis": user_analysis,
#         "previous_response": None  # No previous response for the first model
#     }

#     websocket = websocket_connections.get(request_id)

#     if not websocket:
#         print(f"No WebSocket connection found for request_id: {request_id}")
#     else:
#         print(f"WebSocket connection found for request_id: {request_id}")
    
#     # Sequentially process each role
#     for role in roles:
#         # if websocket:
#         # await websocket.send_json({"message": f"Processing role: {role}"})
#         print(f"Processing role: {role}")
#         response = process_role(input_content, model, headers, role, feedback)
#         # if websocket:
#         #     await websocket.send_json({"message": f"Completed processing role: {role}"})
#         input_content["previous_response"] = response  # Update input for the next role
        

#     # Parse the final response (from Compliance)
#     final_response = parse_user_stories(input_content["previous_response"])

#     # The last role's response is returned
#     return JSONResponse({"final_response": final_response})


async def generate_user_stories(request: Request):
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
    glossary = data['glossary']
    user_analysis = data['user_analysis']
    feedback = data['feedback']
    request_id = data.get("request_id")
    context_image = data.get("context_image")


    print(f"feedback: {feedback}")

    

    image_data = None


   
    if context_image:
        image_data = base64.b64decode(context_image) 
        if image_data:
            print(f"Decoded image size: {len(image_data)} bytes")
    
    # Define the roles in sequence
    roles = ["PO", "SA", "Security", "Compliance"]

    # Initial input to the first role (PO) is based on the original data
    input_content = {
        "vision": vision,
        "mvp": mvp,
        "glossary": glossary,
        "user_analysis": user_analysis,
        "previous_response": None  # No previous response for the first model
    }

    websocket = websocket_connections.get(request_id)

    if not websocket:
        print(f"No WebSocket connection found for request_id: {request_id}")
    else:
        print(f"WebSocket connection found for request_id: {request_id}")
    
    # Sequentially process each role
    for role in roles:
        # if websocket:
        # await websocket.send_json({"message": f"Processing role: {role}"})
        print(f"Processing role: {role}")
        response = process_role(input_content, image_data,  model, headers, role, feedback)
        # if websocket:
        #     await websocket.send_json({"message": f"Completed processing role: {role}"})
        input_content["previous_response"] = response  # Update input for the next role
        # input_content["previous_response"] = summarize_text(response, max_length=20000)

    # Parse the final response (from Compliance)
    final_response = parse_user_stories(input_content["previous_response"])

    # The last role's response is returned
    return JSONResponse({"final_response": final_response})




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

    print(f"feedback: {feedback}")

    # Define the roles in sequence
    roles = ["PO", "SA", "Security", "Compliance"]

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
    
    # Sequentially process each role
    for role in roles:
        # if websocket:
        # await websocket.send_json({"message": f"Processing role: {role}"})
        print(f"Processing role: {role}")
        response = regenerate_process_role(input_content, model, headers, role, feedback)
        # if websocket:
        #     await websocket.send_json({"message": f"Completed processing role: {role}"})
        input_content["previous_response"] = response  # Update input for the next role
        

    # Parse the final response (from Compliance)
    final_response = parse_user_stories(input_content["previous_response"])

    # The last role's response is returned
    return JSONResponse({"final_response": final_response})



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
        stories_with_epics = generate_user_stories_with_epics(vision_text, mvp_text, "", "", model, headers)
    except Exception as e:
        return JSONResponse({'error': f"Error generating user stories: {str(e)}"}, status_code=500)

    # If feedback exists and mentions the response is bad, regenerate
    if feedback and "bad" in feedback.lower():
        # Logic to regenerate the response (for simplicity, here just re-call the function)
        stories_with_epics = generate_user_stories_with_epics(vision_text, mvp_text, "", "", model, headers)

    return JSONResponse({"stories_with_epics": stories_with_epics})



async def upload_csv(request: Request):
    form = await request.form()
    file = form.get("file")
    if not file:
        return JSONResponse({'error': 'No file part'}, status_code=400)
    
    file_path, error = save_uploaded_file(UPLOAD_FOLDER, file)
    
    if error:
        return JSONResponse({'error': error}, status_code=400)
    if file_path:
        csv_data = parse_csv_to_json(file_path)
        return JSONResponse({"stories_with_epics": csv_data})

current_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Starlette(debug=True, middleware=[
    Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
], routes=[
    Route('/api/generate-user-stories', generate_user_stories, methods=['POST']),
    Route('/api/regenerate-user-stories', regenerate_user_stories, methods=['POST']),
    Route('/api/generate-user-stories-by-files', generate_user_stories_by_files, methods=['POST']),
    Route('/api/upload-csv', upload_csv, methods=['POST']),
    Route('/api/check-user-stories-quality', check_user_stories_quality, methods=['POST']),
    WebSocketRoute("/api/ws-chat", websocket_endpoint),
    Mount('/', StaticFiles(directory='dist', html=True), name='static')
])




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0', port=8000)