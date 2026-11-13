from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pymongo.errors import PyMongoError

from app.database import profiles

app = FastAPI(title="Python Profile Manager")
HTML_FILE = Path(__file__).parent / "templates" / "index.html"
USER_ID = 1


class Profile(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=200)
    job_title: str = Field(default="", max_length=100)
    bio: str = Field(default="", max_length=500)


@app.get("/")
def home():
    return FileResponse(HTML_FILE)


@app.get("/get-profile")
def get_profile():
    try:
        document = profiles.find_one({"_id": USER_ID})
    except PyMongoError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    if document is None:
        return {"name": "", "email": "", "job_title": "", "bio": ""}
    return {key: document.get(key, "") for key in Profile.model_fields}


@app.post("/update-profile")
def update_profile(profile: Profile):
    try:
        profiles.update_one(
            {"_id": USER_ID},
            {"$set": profile.model_dump()},
            upsert=True,
        )
    except PyMongoError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"message": "Profile saved successfully"}
