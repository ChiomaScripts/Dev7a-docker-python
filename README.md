# Python Profile Manager

A small FastAPI and MongoDB application for Docker learning exercises.

## Setup

```bash
uv init --bare
uv add fastapi uvicorn pymongo
uv run uvicorn app.main:app --reload
```

The app is available at http://127.0.0.1:8000 and the API docs at http://127.0.0.1:8000/docs.

MongoDB must be running and accessible at `mongodb://localhost:27017`, or set `MONGO_URI` to another MongoDB connection URI. No Docker configuration is included yet.
