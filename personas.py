# import json
# from fastapi import HTTPException, Request
# from fastapi.responses import JSONResponse
# from motor.motor_asyncio import AsyncIOMotorClient
# from bson import ObjectId

# MONGO_URI = "mongodb+srv://reactblog:NDpmDZiPiC3goILD@cluster0.7na1v62.mongodb.net/MVP?retryWrites=true&w=majority&appName=Cluster0"
# client = AsyncIOMotorClient(MONGO_URI)
# db = client["MVP"]  # Database name
# personas_collection = db["personas"]


# # Example function to fetch personas
# def convert_objectid(persona):
#     persona["_id"] = str(persona["_id"])  # Convert ObjectId to string
#     return persona

# async def get_personas(request):
#     personas_cursor = personas_collection.find()  # Get the async cursor
#     personas_list = await personas_cursor.to_list(length=None)  # Await and convert to list
#     personas_list = [convert_objectid(persona) for persona in personas_list]
#     # Wrap the list in a JSONResponse before returning
#     return JSONResponse(content=personas_list)


# # Handler to add a new persona
# async def add_persona(request):
#     data = await request.json()
#     result = await personas_collection.insert_one(data)
#     return JSONResponse({"message": "Persona added", "id": str(result.inserted_id)})

# # Handler to delete persona
# async def delete_persona(request: Request):
#     persona_id = request.path_params.get("persona_id")  # Extract persona_id from request params
#     if not ObjectId.is_valid(persona_id):  # Ensure it's a valid ObjectId
#         return JSONResponse({"error": "Invalid persona ID"}, status_code=400)

#     result = await personas_collection.delete_one({"_id": ObjectId(persona_id)})
    
#     if result.deleted_count == 0:
#         return JSONResponse({"error": "Persona not found"}, status_code=404)
    
#     return JSONResponse({"message": "Persona deleted successfully"})

# # Handler to update persona
# async def update_persona(request: Request):
#     persona_id = request.path_params.get("persona_id")  # Extract persona_id from URL

#     if not ObjectId.is_valid(persona_id):  # Ensure it's a valid ObjectId
#         return JSONResponse({"error": "Invalid persona ID"}, status_code=400)

#     update_data = await request.json()  # Extract JSON data from request body

#     result = await personas_collection.update_one(
#         {"_id": ObjectId(persona_id)},  # Find by ID
#         {"$set": update_data}  # Update data
#     )

#     if result.matched_count == 0:
#         return JSONResponse({"error": "Persona not found"}, status_code=404)

#     return JSONResponse({"message": "Persona updated successfully"})


import json
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# In-memory storage for personas
personas = [
    {
        "_id": "1",
        "name": "PO",
        "role": "Product Owner",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "As a Product Owner, your task is to generate high-quality user stories based on the provided project requirements and vision. Ensure that the stories follow the INVEST principle (Independent, Negotiable, Valuable, Estimable, Small, and Testable)."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "As a Product Owner, your task is to prioritize user stories based on business value, dependencies, and stakeholder needs. Use prioritization frameworks like MoSCoW or WSJF to justify ranking."}
        ]
    },
    {
        "_id": "2",
        "name": "SA",
        "role": "Solution Architect",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "As a Solution Architect, your task is to generate user stories that capture architectural decisions, trade-offs, and system constraints while ensuring alignment with business goals."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "As a Solution Architect, your task is to prioritize architectural components and decisions based on scalability, security, and maintainability considerations."}
        ]
    },
    {
        "_id": "3",
        "name": "QA",
        "role": "Quality Assurance",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "As a Quality Assurance expert, your task is to generate detailed test cases and acceptance criteria based on the given user stories to ensure comprehensive test coverage."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "As a Quality Assurance expert, your task is to prioritize test scenarios and automation efforts based on risk, critical functionality, and defect history."}
        ]
    },
    {
        "_id": "4",
        "name": "Developer",
        "role": "developer",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "As a Developer, your task is to refine user stories by adding technical details, defining acceptance criteria, and breaking down stories into manageable development tasks."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "As a Developer, your task is to prioritize development tasks based on dependencies, complexity, and potential impact on project timelines."}
        ]
    },
    {
        "_id": "5",
        "name": "Compliance",
        "role": "Compliance Agent",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "As a Compliance Agent, your task is to generate compliance-related user stories that address regulatory requirements such as GDPR, HIPAA, and industry best practices."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "As a Compliance Agent, your task is to prioritize compliance tasks and reviews based on legal risk, business impact, and industry regulations."}
        ]
    },
    {
        "_id": "6",
        "name": "Security",
        "role": "Security Expert",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "As a Security Expert, your task is to generate security-related user stories focusing on threat modeling, vulnerability mitigation, and secure coding practices."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "As a Security Expert, your task is to prioritize security enhancements and vulnerability fixes based on threat severity, exploitability, and business risk."}
        ]
    },
    {
        "_id": "7",
        "name": "AI Strategist",
        "role": "AI Strategist",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "Act as the forward-thinking strategist who identifies high-impact use cases for AI, crafts a roadmap for integration, and prioritizes projects based on their potential business value. This role involves translating business challenges into actionable AI opportunities, fostering cross-departmental collaboration, and continuously reassessing the strategy to stay ahead in a rapidly evolving technological landscape."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "Act as the forward-thinking strategist who identifies high-impact use cases for AI, crafts a roadmap for integration, and prioritizes projects based on their potential business value. This role involves translating business challenges into actionable AI opportunities, fostering cross-departmental collaboration, and continuously reassessing the strategy to stay ahead in a rapidly evolving technological landscape."}
        ]
    },
    {
        "_id": "8",
        "name": "DSEL",
        "role": "Data Science and Engineering Lead",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "Act as the technical linchpin responsible for architecting and deploying AI solutions. This persona ensures that data infrastructure, model development, and system integration are robust and scalable. They collaborate closely with the AI Strategist and Business Process Owner to align technical execution with strategic objectives while maintaining best practices in model governance and system reliability."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "Act as the technical linchpin responsible for architecting and deploying AI solutions. This persona ensures that data infrastructure, model development, and system integration are robust and scalable. They collaborate closely with the AI Strategist and Business Process Owner to align technical execution with strategic objectives while maintaining best practices in model governance and system reliability."}
        ]
    },
    {
        "_id": "9",
        "name": "CMA",
        "role": "Change Management Agent",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "Act as the catalyst for cultural and organizational transformation. This role focuses on managing the human aspects of AI adoption by facilitating training programs, addressing resistance to change, and ensuring clear communication across teams. They help bridge the gap between technical innovation and everyday operations, ensuring that employees are engaged and empowered to work effectively with new AI-driven processes."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "Act as the catalyst for cultural and organizational transformation. This role focuses on managing the human aspects of AI adoption by facilitating training programs, addressing resistance to change, and ensuring clear communication across teams. They help bridge the gap between technical innovation and everyday operations, ensuring that employees are engaged and empowered to work effectively with new AI-driven processes."}
        ]
    },
    {
        "_id": "10",
        "name": "BPO",
        "role": "Business Process Owner",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "Act as the expert who understands the nuances of core business operations and translates them into requirements for AI solutions. This persona collaborates with both technical teams and executive leadership to ensure that AI initiatives are tailored to address specific operational challenges, improve efficiency, and create measurable value for the business. Their insights help ground AI projects in real-world needs and practical applications."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "Act as the expert who understands the nuances of core business operations and translates them into requirements for AI solutions. This persona collaborates with both technical teams and executive leadership to ensure that AI initiatives are tailored to address specific operational challenges, improve efficiency, and create measurable value for the business. Their insights help ground AI projects in real-world needs and practical applications."}
        ]
    },
    {
        "_id": "11",
        "name": "SCO",
        "role": "Security and Compliance Officer",
        "default_icon": "default",
        "tasks": [
            {"taskName": "user_story_generation", "taskLabel": "User Story Generation", "prompt": "Act as the guardian of ethical standards, security and regulatory compliance throughout the AI adoption journey. This role ensures that AI initiatives adhere to legal frameworks and ethical guidelines, mitigating risks related to bias, privacy, security, and transparency. By establishing clear protocols and oversight mechanisms, this persona builds trust both internally and externally, reinforcing the companyâ€™s commitment to responsible AI practices."},
            {"taskName": "prioritization", "taskLabel": "Prioritization", "prompt": "Act as the guardian of ethical standards, security and regulatory compliance throughout the AI adoption journey. This role ensures that AI initiatives adhere to legal frameworks and ethical guidelines, mitigating risks related to bias, privacy, security, and transparency. By establishing clear protocols and oversight mechanisms, this persona builds trust both internally and externally, reinforcing the companyâ€™s commitment to responsible AI practices."}
        ]
    },
]

def convert_objectid(persona):
    persona["_id"] = str(persona["_id"])  # Ensure ID is string
    return persona

# Example function to fetch personas
async def get_personas(request):
    return JSONResponse(content=personas)

# Handler to add a new persona
async def add_persona(request):
    data = await request.json()
    data["_id"] = str(len(personas) + 1)  # Generate a simple unique ID
    personas.append(data)
    print(personas)
    return JSONResponse({"message": "Persona added", "id": data["_id"]})

# Handler to delete persona
async def delete_persona(request: Request):
    persona_id = request.path_params.get("persona_id")
    global personas
    new_personas = [p for p in personas if p["_id"] != persona_id]
    
    if len(new_personas) == len(personas):
        return JSONResponse({"error": "Persona not found"}, status_code=404)
    
    personas = new_personas
    return JSONResponse({"message": "Persona deleted successfully"})

# Handler to update persona
async def update_persona(request: Request):
    persona_id = request.path_params.get("persona_id")
    update_data = await request.json()
    
    for index, persona in enumerate(personas):
        if persona["_id"] == persona_id:
            personas[index].update(update_data)
            return JSONResponse({"message": "Persona updated successfully"})
    
    return JSONResponse({"error": "Persona not found"}, status_code=404)
