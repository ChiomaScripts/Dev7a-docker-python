from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pymongo.errors import PyMongoError

from app.database import profiles


app = FastAPI(title="Python Girls That Code")

BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "templates" / "index.html"
STATIC_DIR = BASE_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# Define the structure of a profile
class Profile(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=200)
    job_title: str = Field(default="", max_length=100)
    bio: str = Field(default="", max_length=500)
    skills: str = Field(default="", max_length=500)


# Convert MongoDB documents into JSON-friendly dictionaries
def serialize_profile(document):
    return {
        "id": str(document["_id"]),
        "name": document.get("name", ""),
        "email": document.get("email", ""),
        "job_title": document.get("job_title", ""),
        "bio": document.get("bio", ""),
        "skills": document.get("skills", ""),
    }


# Validate a MongoDB document ID
def parse_profile_id(profile_id: str):
    try:
        return ObjectId(profile_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid profile ID"
        )


# Serve the frontend
@app.get("/")
def home():
    return FileResponse(HTML_FILE)


# CREATE — Add a new profile
@app.post("/profiles", status_code=201)
def create_profile(profile: Profile):
    try:
        result = profiles.insert_one(profile.model_dump())
        document = profiles.find_one({"_id": result.inserted_id})
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        ) from exc

    return serialize_profile(document)


# READ — List all profiles
@app.get("/profiles")
def list_profiles():
    try:
        documents = profiles.find().sort("name", 1)
        return [serialize_profile(doc) for doc in documents]
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        ) from exc


# READ — Retrieve one profile
@app.get("/profiles/{profile_id}")
def get_profile(profile_id: str):
    object_id = parse_profile_id(profile_id)

    try:
        document = profiles.find_one({"_id": object_id})
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        ) from exc

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return serialize_profile(document)


# UPDATE — Modify an existing profile
@app.put("/profiles/{profile_id}")
def update_profile(profile_id: str, profile: Profile):
    object_id = parse_profile_id(profile_id)

    try:
        result = profiles.update_one(
            {"_id": object_id},
            {"$set": profile.model_dump()}
        )
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        ) from exc

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return {"message": "Profile updated successfully 💜"}


# DELETE — Remove an existing profile
@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str):
    object_id = parse_profile_id(profile_id)

    try:
        result = profiles.delete_one({"_id": object_id})
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        ) from exc

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return {"message": "Profile deleted successfully"}