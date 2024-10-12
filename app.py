from fastapi import FastAPI
from routers import items, clock_in
from database import test_connection

app = FastAPI()

# Include routers
app.include_router(items.router)
app.include_router(clock_in.router)


@app.on_event("startup")
async def startup_event():
    await test_connection()

# Your route definitions go here

# Root endpoint
@app.get("/")
async def root():
    return {"message": "FastAPI with MongoDB"}
