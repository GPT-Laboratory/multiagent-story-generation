# API to create a new project
import os
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from personas import personas_list
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["MVP"]  # Database name
collection = db["projects"]  # Collection name
user_stories_collection = db["user_stories"]
personas_collection = db["personas"]


# Update Story API
async def update_story(request):
    try:
        data = await request.json()
        story_id = data.get("_id")
        if not story_id:
            return JSONResponse({"error": "Story ID is required"}, status_code=400)

        # Query to find the document where stories array contains the given story_id
        filter_query = {"stories": {"$elemMatch": {"_id": ObjectId(story_id)}}}
        update_query = {
            "$set": {
                "stories.$.user_story": data.get("user_story"),
                "stories.$.description": data.get("description"),
                "stories.$.epic": data.get("epic"),
                "stories.$.suggestion": data.get("suggestion")
            }
        }

        result = await user_stories_collection.update_one(filter_query, update_query)

        if result.modified_count == 0:
            return JSONResponse({"error": "User story not found or no changes made"}, status_code=404)

        return JSONResponse({"message": "User story updated successfully"})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)



async def delete_user_story_version(request):
    story_id = request.path_params["story_id"]
    if not ObjectId.is_valid(story_id):
        return JSONResponse({"detail": "Invalid story ID"}, status_code=400)
    
    result = await user_stories_collection.delete_one({"_id": ObjectId(story_id)})
    
    if result.deleted_count == 0:
        return JSONResponse({"detail": "User story not found"}, status_code=404)
    
    return JSONResponse({"message": "User story deleted successfully", "story_id": story_id})


async def delete_user_story(request: Request):
    story_id = request.path_params["story_id"]

    # Find and remove user story from user_stories_collection
    result = await user_stories_collection.update_one(
        {"stories": {"$elemMatch": {"_id": ObjectId(story_id)}}},
        {"$pull": {"stories": {"_id": ObjectId(story_id)}}}
    )

    if result.modified_count == 0:
        return JSONResponse({"error": "Story not found or deletion failed"}, status_code=404)

    return JSONResponse({"message": "User story deleted successfully"}, status_code=200)

async def fetch_projects(request):
    try:
        user_id = request.query_params.get("user_id")  # Get user_id from query params
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        projects_cursor = collection.find({"user_id": user_id})  # Filter by user_id
        projects = await projects_cursor.to_list(length=None)  

        return JSONResponse(content=[project_serializer(p) for p in projects])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {str(e)}")

async def get_all_user_stories(request):
    try:
        print("Fetching all user stories...")  # Debugging

        # Fetch all user stories from the collection
        user_stories_list = await user_stories_collection.find().to_list(length=None)

        if not user_stories_list:
            return JSONResponse(content={"message": "No user stories found"}, status_code=404)

        # Convert all ObjectId fields to strings
        user_stories_list = convert_objectid_to_str(user_stories_list)
        # print(user_stories_list)  # Debugging

        return JSONResponse(content=user_stories_list)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def get_user_stories(request):
    try:
        project_id = request.path_params.get("project_id")
        print(f"Fetching user stories for project_id: {project_id}")  # Debugging

        if not project_id:
            return JSONResponse(content={"error": "Project ID is required"}, status_code=400)

        # Fetch all user stories with the given project_id
        user_stories_cursor = user_stories_collection.find({"project_id": project_id})
        user_stories_list = await user_stories_cursor.to_list(length=None)  # Convert cursor to list

        if not user_stories_list:
            return JSONResponse(content={"message": "No user stories found for this project"}, status_code=404)

        # Convert MongoDB ObjectId to string
        for entry in user_stories_list:
            entry["_id"] = str(entry["_id"])
            for story in entry["stories"]:
                story["_id"] = str(story["_id"])

        return JSONResponse(content=user_stories_list)  # Return the full list

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


async def create_project(request):
    data = await request.json()
    project_name = data.get("project_name")
    user_id = data.get("user_id")

    if not project_name:
        raise HTTPException(status_code=400, detail="Project name is required")

    # Create a new project
    new_project = {"name": project_name, "user_id": user_id}
    result = await collection.insert_one(new_project)
    project_id = str(result.inserted_id)  # Convert ObjectId to string

    # Attach project_id and generate a new ObjectId for each persona
    personas_with_project = [
        {**persona, "_id": ObjectId(), "project_id": project_id} for persona in personas_list
    ]

    # Insert personas into MongoDB
    await personas_collection.insert_many(personas_with_project)

    return JSONResponse({
        "message": "Project created with default personas",
        "project_id": project_id,
        # "id": str(result.inserted_id)
    })

def convert_objectid_to_str(data):
    if isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    return data

async def delete_project(request):
    project_id = request.path_params["project_id"]
    
    try:
        # Delete the project
        project_result = await collection.delete_one({"_id": ObjectId(project_id)})
        if project_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete all user stories related to this project
        user_stories_result = await user_stories_collection.delete_many({"project_id": project_id})

        # Delete all personas related to this project
        personas_result = await personas_collection.delete_many({"project_id": project_id})

        return JSONResponse({
            "message": "Project and related user stories deleted",
            "project_deleted": project_result.deleted_count,
            "user_stories_deleted": user_stories_result.deleted_count,
            "personas_deleted": personas_result.deleted_count
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project and user stories: {str(e)}")
# helper function
# Helper function to convert MongoDB document to dictionary
def project_serializer(project):
    return {
        "id": str(project["_id"]),  # Convert ObjectId to string
        "project_name": project["name"]
    }