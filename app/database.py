import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

# Locate and load the project's .env file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Retrieve MongoDB configuration
MONGO_URI = os.environ["MONGO_URI"]
DATABASE_NAME = os.getenv("MONGO_DB_NAME", "user-account")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "users")

# Initialise MongoDB client
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=3000
)

# Select database and collection
database = client[DATABASE_NAME]
profiles = database[COLLECTION_NAME]