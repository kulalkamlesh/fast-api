import motor.motor_asyncio
from bson import ObjectId
from datetime import datetime
import asyncio
import ssl
from fastapi import FastAPI

# MongoDB connection details for MongoDB Atlas instance
MONGO_DETAILS = "mongodb+srv://kasthurikulal883:zPnVcscuszVqE5XS@demo.hawle.mongodb.net/development?retryWrites=true&w=majority&tls=true"

# Create a MongoDB client with context manager
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

# Specify the database
database = client.development  # Ensure this matches your database name

# Collections
items_collection = database.get_collection("items")
clockin_collection = database.get_collection("clock_in")

# Helper function to parse MongoDB response
def item_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "email": item["email"],
        "item_name": item["item_name"],
        "quantity": item["quantity"],
        "expiry_date": item["expiry_date"],
        "insert_date": item["insert_date"],
    }

# Test connection and print success message
async def test_connection():
    try:
        # Perform a simple operation to test the connection
        await items_collection.find_one()
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

# Create FastAPI app
app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the API!"}

# Run the test connection function
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_connection())
    # Run the FastAPI app
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
