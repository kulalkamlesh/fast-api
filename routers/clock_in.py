from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from models import ClockInModel, UpdateClockInModel
from database import clockin_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter()

# Function to convert ObjectId to string
def convert_objectid_to_str(clock_in):
    clock_in["_id"] = str(clock_in["_id"])  # Convert ObjectId to string
    return clock_in



# Filter clock-in records
@router.get("/clock-in/filter")
async def filter_clock_in(email: str = None, location: str = None, insert_datetime: str = None):
    query = {}
    if email:
        query["email"] = email
    if location:
        query["location"] = location
    if insert_datetime:
        query["insert_datetime"] = insert_datetime
    
    clock_ins = await clockin_collection.find(query).to_list(100)
    return [convert_objectid_to_str(clock_in) for clock_in in clock_ins]


# Create a clock-in record
@router.post("/clock-in")
async def create_clock_in(clock_in: ClockInModel = Body(...)):
    clock_in_data = jsonable_encoder(clock_in)
    clock_in_data["insert_datetime"] = datetime.now()
    new_clock_in = await clockin_collection.insert_one(clock_in_data)
    created_clock_in = await clockin_collection.find_one({"_id": new_clock_in.inserted_id})
    return convert_objectid_to_str(created_clock_in)

# Get clock-in record by ID
@router.get("/clock-in/{id}")
async def get_clock_in(id: str):
    clock_in = await clockin_collection.find_one({"_id": ObjectId(id)})
    if clock_in:
        return convert_objectid_to_str(clock_in)
    raise HTTPException(status_code=404, detail=f"Clock-in record {id} not found")

# Update clock-in record by ID
@router.put("/clock-in/{id}")
async def update_clock_in(id: str, clock_in: UpdateClockInModel = Body(...)):
    # Check if the provided ID is a valid ObjectId
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    
    # Create a dictionary of the fields to update, excluding None values
    clock_in_data = {k: v for k, v in clock_in.dict().items() if v is not None}
    
    # Attempt to update the clock-in record
    updated_clock_in = await clockin_collection.update_one({"_id": ObjectId(id)}, {"$set": clock_in_data})
    
    # Check if the record was updated
    if updated_clock_in.modified_count == 1:
        # Return the updated record
        updated_record = await clockin_collection.find_one({"_id": ObjectId(id)})
        return convert_objectid_to_str(updated_record)
    
    # If no records were modified, the ID may not have matched any document
    raise HTTPException(status_code=404, detail=f"Clock-in record {id} not found")


# Delete clock-in record by ID
@router.delete("/clock-in/{id}")
async def delete_clock_in(id: str):
    deleted_clock_in = await clockin_collection.delete_one({"_id": ObjectId(id)})
    if deleted_clock_in.deleted_count == 1:
        return {"status": "Clock-in record deleted"}
    raise HTTPException(status_code=404, detail=f"Clock-in record {id} not found")
