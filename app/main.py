from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pymongo.errors import PyMongoError

from app.database import profiles


# Initialise FastAPI application
app = FastAPI(title="Python Girls That Code")

# Define application paths
BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "templates" / "index.html"
STATIC_DIR = BASE_DIR / "static"

# Serve CSS, images and other static assets
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# Temporary identifier for our single-profile application
USER_ID = 1


# Define and validate the profile data
class Profile(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=200)
    job_title: str = Field(default="", max_length=100)
    bio: str = Field(default="", max_length=500)
    skills: str = Field(default="", max_length=500)


# Serve the application's HTML page
@app.get("/")
def home():
    return FileResponse(HTML_FILE)


# Retrieve an existing profile from MongoDB
@app.get("/get-profile")
def get_profile():
    try:
        document = profiles.find_one({"_id": USER_ID})
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        ) from exc

    if document is None:
        return {
            "name": "",
            "email": "",
            "job_title": "",
            "bio": "",
            "skills": ""
        }

    return {
        key: document.get(key, "")
        for key in Profile.model_fields
    }


# Create or update a profile in MongoDB
@app.post("/update-profile")
def update_profile(profile: Profile):
    try:
        profiles.update_one(
            {"_id": USER_ID},
            {"$set": profile.model_dump()},
            upsert=True,
        )
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        ) from exc

    return {"message": "Profile saved successfully 💜"}