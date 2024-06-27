from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# Connection string to your MongoDB instance
MONGO_DETAILS = "mongodb://localhost:27017/"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.wallet_app

transactions = database.get_collection("transactions")
users = database.get_collection("users")
budgets = database.get_collection("budgets")
