from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
import os
import uvicorn

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.ai_safety_log_api_db
collection = db.incidents

# Pydantic Models
class IncidentBase(BaseModel):
    title: str
    description: str
    severity: str
    reported_at: datetime = datetime.utcnow()

class IncidentData(IncidentBase):
    id: str

class IncidentResponse(BaseModel):
    status_code: int
    message: str
    data: IncidentData | None = None

class IncidentListResponse(BaseModel):
    status_code: int
    message: str
    data: list[IncidentData]

# Utility function to convert MongoDB document
async def serialize_incident(document) -> IncidentData:
    return IncidentData(
        id = str(document["_id"]), 
        title=document["title"],
        description=document["description"],
        severity=document["severity"],
        reported_at=document["reported_at"]
    )

# API Endpoints
@app.get("/", response_model=dict)
async def index():
    return {"message": "Welcome to the AI Safety Log API"}

# GET /incidents - Retrieve all incidents
@app.get("/incidents", response_model=IncidentListResponse)
async def get_incidents():
    incidents = await collection.find().to_list(25)
    
    return IncidentListResponse(
        status_code=200,
        message="All Incidents retrieved",
        data=[await serialize_incident(doc) for doc in incidents]
    )


# POST /incidents - Create a new incident
@app.post("/incidents", response_model=IncidentResponse)
async def create_incident(incident: IncidentBase):
    if incident.severity not in ["Low", "Medium", "High"]:
        raise HTTPException(status_code=400, detail="Invalid severity level")
    new_incident = await collection.insert_one(incident.dict())
    created_incident = await collection.find_one({"_id": new_incident.inserted_id})
    return IncidentResponse(
        status_code=201,
        message="Incident successfully created",
        data=await serialize_incident(created_incident)
    )
    

# GET /incidents/{id} - Retrieve a specific incident
@app.get("/incidents/{id}", response_model=IncidentResponse)
async def get_incident(id: str):
    incident = await collection.find_one({"_id": ObjectId(id)})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    return IncidentResponse(
        status_code=200,
        message="Incident successfully retrieved",
        data=await serialize_incident(incident)
    )

# DELETE /incidents/{id} - Delete an incident
@app.delete("/incidents/{id}", response_model=IncidentResponse)
async def delete_incident(id: str):
    result = await collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse(
        status_code=200,
        message="Incident successfully deleted",
        data=None
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)