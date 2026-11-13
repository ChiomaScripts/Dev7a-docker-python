# 1. Start from an image containing Python 3.13
FROM python:3.13-slim

# 2. Set the working directory inside the container
WORKDIR /home/app

# 3. Copy our dependency definition and lockfile
COPY pyproject.toml uv.lock ./

# 4. Install uv and our locked Python dependencies
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev --no-install-project

# 5. Copy our FastAPI application into the container
COPY ./app ./app

# 6. Document the port our application listens on
EXPOSE 8000

# 7. Start the FastAPI application
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]