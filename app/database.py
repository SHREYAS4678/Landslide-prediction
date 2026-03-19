from motor.motor_asyncio import AsyncIOMotorClient

# Using a local MongoDB for development, or a mocked interface if not available
MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.landslide_db

user_collection = database.get_collection("users")
sensor_collection = database.get_collection("sensor_readings")

# Utility functions for DB operations could go here
async def init_db():
    print("MongoDB connection initialized")
