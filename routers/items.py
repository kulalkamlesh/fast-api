from fastapi import APIRouter, Query, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from models import ItemModel, UpdateItemModel
from database import items_collection, item_helper
from bson import ObjectId
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

router = APIRouter()

@router.get("/items/aggregate/")
async def count_items_by_email_and_total() -> Dict[str, Any]:
    # Aggregation pipeline to count items by email
    email_count_pipeline = [
        {
            "$group": {
                "_id": "$email",        # Group by email field
                "count": {"$sum": 1}    # Count the number of occurrences
            }
        },
        {
            "$project": {
                "email": "$_id",       # Include email in the output
                "count": 1,            # Include the count
                "_id": 0                # Exclude the default _id field
            }
        }
    ]

    # Perform the aggregation to get count by email
    email_counts = await items_collection.aggregate(email_count_pipeline).to_list(length=None)

    # Total count of items in the collection
    total_items = await items_collection.count_documents({})

    return {
        "status": "success",
        "message": "Aggregation successful",
        "data": {
            "email_counts": email_counts,
            "total_items": total_items  # Total count of items
        }
    }




@router.get("/items/filter")
async def filter_items(
    email: Optional[str] = None,
    expiry_date: Optional[str] = None,
    insert_date: Optional[str] = None,
    quantity: Optional[int] = Query(None, ge=0)
):
    query = {}

    # Filter by email if provided
    if email:
        query["email"] = email

    # Filter by expiry_date if provided
    if expiry_date:
        # Assuming expiry_date is stored as string in the database
        query["expiry_date"] = expiry_date 
        
    if insert_date:
        query["insert_date"] = insert_date

    # Filter by quantity if provided
    if quantity is not None:
        query["quantity"] = {"$gte": quantity}

    # Log the query for debugging
    print(f"Query: {query}")

    # Fetch the items from the database
    items = await items_collection.find(query).to_list(length=None)

    # Convert _id (ObjectId) to string for each item
    for item in items:
        item["_id"] = str(item["_id"])

    # Return filtered results or raise 404 if no items are found
    if items:
        return {
            "status": "success",
            "message": "Items filtered successfully",
            "data": items
        }

    raise HTTPException(status_code=404, detail="No items found matching the filter criteria")




@router.post("/items", response_description="Item created successfully")
async def create_item(item: ItemModel = Body(...)):
    item_data = jsonable_encoder(item)
    item_data["insert_date"] = datetime.now().date().strftime("%Y-%m-%d")

    # Insert the new item without checking for email existence
    try:
        new_item = await items_collection.insert_one(item_data)
        created_item = await items_collection.find_one({"_id": new_item.inserted_id})

        return {
            "status": "success",
            "message": "Item created successfully",
            "data": item_helper(created_item)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting item: {str(e)}")


# Get item by ID

@router.get("/items/{id}")
async def get_item(id: str):
    try:
        item = await items_collection.find_one({"_id": ObjectId(id)})
        if item:
            return {
                "status": "success",
                "message": "Item retrieved successfully",
                "data": item_helper(item)
            }
        raise HTTPException(status_code=404, detail=f"Item {id} not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Filter items based on email, expiry date, insert date, and quantity

def is_valid_objectid(oid):
    try:
        ObjectId(oid)
        return True
    except Exception:
        return False



@router.put("/items/{id}")
async def update_item(id: str, item: UpdateItemModel = Body(...)):
    item_data = {k: v for k, v in item.dict().items() if v is not None}

    if "expiry_date" in item_data:
        item_data["expiry_date"] = datetime.combine(item_data["expiry_date"], datetime.min.time())

    updated_item = await items_collection.update_one({"_id": ObjectId(id)}, {"$set": item_data})

    if updated_item.modified_count == 1:
        updated_item_data = await items_collection.find_one({"_id": ObjectId(id)})
        return {
            "status": "success",
            "message": "Item updated successfully",
            "data": item_helper(updated_item_data)
        }
    raise HTTPException(status_code=404, detail=f"Item {id} not found")

# Delete item by ID
@router.delete("/items/{id}")
async def delete_item(id: str):
    deleted_item = await items_collection.delete_one({"_id": ObjectId(id)})
    if deleted_item.deleted_count == 1:
        return {
            "status": "success",
            "message": "Item deleted successfully"
        }
    raise HTTPException(status_code=404, detail=f"Item {id} not found")

