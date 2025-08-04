import os
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient



MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["MVP"]  # Database name
project_reports = db["project_reports"]
final_table_prioritizations = db["final_table_prioritizations"]
prioritization_collection = db["prioritization_collection"]


async def get_final_table_prioritization(request):
    story_id = request.path_params["story_id"]
    result = await final_table_prioritizations.find_one({"story_id": story_id})

    if result:
        result["_id"] = str(result["_id"])  # Convert ObjectId to string for JSON response
        return JSONResponse({"data": result})
    else:
        return JSONResponse({"error": "Not found"}, status_code=404)
    

async def get_final_prioritization(request):
    story_id = request.path_params["story_id"]
    result = await prioritization_collection.find_one({"story_id": story_id})

    if result:
        result["_id"] = str(result["_id"])  # Convert ObjectId to string for JSON response
        return JSONResponse({"data": result})
    else:
        return JSONResponse({"error": "Not found"}, status_code=404)