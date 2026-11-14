# Dev7a — Docker for Local Development | Python, FastAPI & MongoDB

**Docker Image Build & Deployment | Container Networking | FastAPI | MongoDB**

Part of my hands-on DevOps engineering portfolio, documenting my progression through containerisation, application deployment, infrastructure automation and cloud technologies.


---

## 01 — Project Overview

This project explores how Docker can be used to establish a local development environment where an application communicates with a database running inside a container.

The original training demo uses a Node.js application alongside MongoDB and Mongo Express. I chose to adapt the implementation using **Python and FastAPI**, building my own application rather than relying entirely on the provided JavaScript source code.

This allowed me to combine my existing Python knowledge with new Docker concepts while gaining practical experience in application development, database integration, container networking and troubleshooting.

The application, **Python Girls That Code**, is a profile management platform where coding enthusiasts can create and manage their profiles, including their names, email addresses, job titles, biographies and technical skills.

The final implementation packages FastAPI into a custom Docker image and runs it alongside MongoDB and Mongo Express on a shared user-defined Docker network. The application can also run directly on Windows for local development.

### Project objectives

- Understand how Docker CLI, Docker Engine and Docker Desktop work together.
- Pull and manage container images from Docker Hub.
- Create and configure Docker containers using command-line arguments.
- Establish communication between containers using a custom Docker network.
- Configure MongoDB authentication using environment variables.
- Publish container ports to make services accessible from the Windows host.
- Connect a locally running Python/FastAPI application to containerised MongoDB, then containerise FastAPI itself.
- Author a Dockerfile and `.dockerignore`, build and tag a custom image, and run the application with runtime configuration.
- Verify access to the containerised application through host-to-container port publishing.
- Verify database connectivity and perform application-level CRUD operations.
- Troubleshoot Docker networking, service availability and configuration issues.

### Technologies used

| Technology            | Purpose                                    |
| :-------------------- | :----------------------------------------- |
| Docker                | Container management and local development |
| Docker Desktop        | Docker Engine integration on Windows       |
| WSL 2 / Linux backend | Linux environment for Docker containers    |
| Python 3.13           | Application programming language           |
| FastAPI               | Backend API framework                      |
| Uvicorn               | ASGI application server                    |
| MongoDB               | NoSQL document database                    |
| Mongo Express         | Web-based MongoDB administration           |
| PyMongo               | Python MongoDB client                      |
| uv                    | Python project and dependency management   |
| HTML, CSS, JavaScript | Application frontend                       |
| Git & GitHub          | Version control and project documentation  |
| VS Code               | Development environment                    |

---

## 02 — Application Architecture

The project was completed in two stages: **local FastAPI development against containerised MongoDB**, followed by **a fully containerised three-service application**. This distinction is important because the correct MongoDB hostname depends on where FastAPI runs.


![Final three-container application architecture](architecture/docker-local-development-workflow.png)

*Figure 1 — Final deployment: browser → published FastAPI port → FastAPI container → MongoDB over `mongo-net`; Mongo Express connects to the same database and is accessible separately from the browser.*

### Final service topology

| Service | Runtime | Internal address | Host access |
| :-- | :-- | :-- | :-- |
| Python Girls That Code | Custom FastAPI Docker image | `python-girls-app:8000` | `localhost:8000` via `-p 8000:8000` |
| MongoDB | `mongo` image | `chioma_mongodb:27017` | `localhost:27017` only when explicitly published for local Python development |
| Mongo Express | `techworldwithnana/mongo-express` | `chioma_mongoexp:8081` | `localhost:8081` via published port |

The three containers share **`mongo-net`**, a user-defined bridge network. Docker's built-in name resolution lets FastAPI and Mongo Express reach MongoDB at `chioma_mongodb:27017` without exposing the database to the host. Publishing ports is needed for services that the **Windows browser or host applications** must reach.

**Key distinction:** `localhost` always means the machine or container making the connection. While FastAPI ran on Windows, its MongoDB URI used `127.0.0.1:27017`. Once FastAPI ran inside its own container, that same address would point back to the FastAPI container, so the URI changed to `chioma_mongodb:27017`.

---

## 03 — Preparing the Python Application

Rather than cloning the Node.js application from the training demonstration, I developed a Python-based alternative using FastAPI.

The project was initialised using `uv`, with FastAPI, Uvicorn and PyMongo installed as application dependencies.

```bash
uv init --bare
uv add fastapi uvicorn pymongo

```

The `--bare` option allowed me to initialise the Python project without generating the default starter application structure, giving me more control over how the project was organised.

### Python version compatibility

During setup, I encountered a Python version compatibility issue.

The project's initial Python requirement did not match the Python 3.13 interpreter I wanted to use.

I resolved this by configuring the project to use Python 3.13, recreating its virtual environment and synchronising its dependencies.

```bash
uv python pin 3.13
uv venv --python 3.13 --clear
uv sync

```

I verified the interpreter using:

```bash
uv run python --version

```

This introduced me to Python interpreter pinning, project-level Python requirements, virtual environments and dependency resolution using `uv`.

### Application structure

```text
Dev7a-docker-python/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── css/
│       │   └── styles.css
│       └── images/
│           └── coding-girl.png
│
├── Dockerfile
├── .dockerignore
├── .env                  # Local Windows configuration; not committed
├── .env.docker           # Container runtime configuration; not committed
├── .env.example          # Sanitised template, if added
├── architecture/
│   └── docker-local-development-workflow.png
├── evidence/             # 13 sanitised screenshots (see Section 15)
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md

```

The application separates API logic, database configuration, frontend templates and static assets.

The `.env` file contains local configuration and is excluded from Git to prevent credentials from being committed.

---

## 04 — Understanding Docker Desktop on Windows

My first Docker-related issue occurred while attempting to download the MongoDB image.

```bash
docker pull mongo

```

The command initially failed because the Docker CLI could not connect to the Docker Engine.

The error referenced the Docker Desktop Linux Engine named pipe:

```text
dockerDesktopLinuxEngine
The system cannot find the file specified.

```

### Investigation

This helped me understand that Docker is not a single standalone program.

Its components perform different responsibilities:

| Component      | Responsibility                                                          |
| :------------- | :---------------------------------------------------------------------- |
| Docker CLI     | Accepts commands such as `docker pull`, `docker run` and `docker ps`    |
| Docker Engine  | Manages images, containers, networks and other Docker resources         |
| Docker Desktop | Provides the Windows application and manages its Docker environment     |
| WSL 2 backend  | Supplies a Linux environment for running Linux containers when selected |

Linux containers depend on Linux kernel functionality, including namespaces and cgroups.

Docker Desktop makes this possible on Windows by running a Linux backend, commonly using WSL 2.

### Resolution

After starting Docker Desktop and allowing its engine to initialise, I repeated the command.

```bash
docker pull mongo

```

The MongoDB image download proceeded successfully.

**Key learning:** Installing the Docker CLI does not necessarily mean that a running Docker Engine is available to execute commands.

### Implementation evidence

**Figure 2 — Page 1 — Docker CLI initially unable to reach the Linux Engine, followed by a successful MongoDB image pull.**

![Docker CLI initially unable to reach the Linux Engine, followed by a successful MongoDB image pull.](evidence/01-docker-engine-recovery.png)

---


## 05 — Pulling and Verifying Docker Images

With Docker Desktop running, I downloaded the MongoDB image from Docker Hub.

```bash
docker pull mongo

```

I also downloaded the Mongo Express image used in the training demonstration:

```bash
docker pull techworldwithnana/mongo-express

```

MongoDB provides the database service, while Mongo Express provides a browser-based interface for viewing databases, collections and documents.

I verified the downloaded images using:

```bash
docker images

```

This command displays locally available Docker images, including their repository names, tags and sizes.

An important distinction is that **an image is not the same as a running container**.

An image is the packaged filesystem and configuration used to create containers. A container is an instance created from that image.

### Implementation evidence

**Figure 3 — Page 2 — Local Docker image list confirming MongoDB and Mongo Express were downloaded.**

![Local Docker image list confirming MongoDB and Mongo Express were downloaded.](evidence/02-downloaded-docker-images.png)

---


## 06 — Creating a Custom Docker Network

The next step was establishing communication between MongoDB and Mongo Express.

I created a dedicated Docker network:

```bash
docker network create mongo-net

```

Both containers were then attached to this network.

### Why use a custom Docker network?

A user-defined bridge network allows containers to communicate directly using their container names.

For example, Mongo Express can connect to:

```text
chioma_mongodb:27017

```

Docker resolves `chioma_mongodb` to the MongoDB container's internal network address.

This avoids relying on container IP addresses that may change when containers are recreated.

### Internal communication versus published ports

Containers connected to the same user-defined bridge network can communicate through their internal ports without those ports being published to the host.

Publishing a port serves a different purpose: it allows a connection originating outside that Docker network, such as one from a Windows application, to reach the container.

This became especially relevant when connecting my locally running FastAPI application to MongoDB.

### Implementation evidence

**Figure 4 — Page 2 — Creation and verification of the user-defined `mongo-net` bridge network.**

![Creation and verification of the user-defined `mongo-net` bridge network.](evidence/03-custom-docker-network.png)

---


## 07 — Running MongoDB in a Container

I started MongoDB in detached mode, configured its initial administrator credentials and attached it to the custom Docker network.

The following example uses placeholder credentials rather than real project secrets.

```bash
docker run -d \
  -e MONGO_INITDB_ROOT_USERNAME=<mongo-admin> \
  -e MONGO_INITDB_ROOT_PASSWORD=<mongo-password> \
  --name chioma_mongodb \
  --net mongo-net \
  -p 127.0.0.1:27017:27017 \
  mongo

```

### Understanding the arguments

| Argument     | Purpose                                              |
| :----------- | :--------------------------------------------------- |
| `docker run` | Creates and starts a container from an image         |
| `-d`         | Runs the container in detached mode                  |
| `-e`         | Supplies an environment variable                     |
| `--name`     | Assigns a recognisable container name                |
| `--net`      | Connects the container to a specified Docker network |
| `-p`         | Publishes a container port to the host               |
| `mongo`      | Specifies the Docker image                           |

The MongoDB image supports initial root account configuration through:

- `MONGO_INITDB_ROOT_USERNAME`
- `MONGO_INITDB_ROOT_PASSWORD`

These variables initialise the administrator account when MongoDB starts with an uninitialised data directory.

The application database was subsequently created through Mongo Express.

### Understanding port publishing

The mapping:

```bash
-p 127.0.0.1:27017:27017

```

means:

**Accept connections arriving at port 27017 on the Windows host's loopback interface and forward them to port 27017 inside the MongoDB container.**

The first port represents the host port, while the second represents the container port.

Binding to `127.0.0.1` limits the published port to local access, which is preferable for this development environment.

---

## 08 — Running Mongo Express

Mongo Express was started as a separate container on the same Docker network.

Its MongoDB connection was configured using an environment variable containing the database connection string.

```bash
docker run -d \
  -p 127.0.0.1:8081:8081 \
  -e ME_CONFIG_MONGODB_URL="mongodb://<mongo-admin>:<mongo-password>@chioma_mongodb:27017/?authSource=admin" \
  -e ME_CONFIG_BASICAUTH_USERNAME=<ui-user> \
  -e ME_CONFIG_BASICAUTH_PASSWORD=<ui-password> \
  --net mongo-net \
  --name chioma_mongoexp \
  techworldwithnana/mongo-express

```

### Understanding the MongoDB connection string

```text
mongodb://username:password@hostname:port/?authSource=admin

```

Its components are:

- `mongodb://` — MongoDB connection protocol.
- `username:password` — database authentication credentials.
- `hostname` — the MongoDB container name, `chioma_mongodb`.
- `27017` — MongoDB's default listening port.
- `authSource=admin` — specifies the authentication database for the root account.

The Mongo Express Basic Authentication credentials are separate from the credentials used to authenticate with MongoDB.

### Accessing Mongo Express

With port 8081 published, the web interface was accessible from the Windows browser at:

```text
http://localhost:8081

```

I used Mongo Express to create and inspect the application's database and `users` collection.

### Implementation evidence

**Figure 5 — Page 3 — Mongo Express successfully opened in the browser, showing the `user-account` database.**

![Mongo Express successfully opened in the browser, showing the `user-account` database.](evidence/04-mongo-express-database.png)

---


## 09 — Verifying Running Containers and Logs

After starting the containers, I inspected their runtime status using:

```bash
docker ps

```

This displayed the running containers, image names, container IDs, uptime and port mappings.

I also inspected the Mongo Express logs using:

```bash
docker logs chioma_mongoexp

```

The logs confirmed that Mongo Express had started its web server and was listening on port 8081.

```text
Mongo Express server listening at http://0.0.0.0:8081

```

Here, `0.0.0.0` indicates that the application is listening on all available network interfaces inside its container.

The Docker port mapping determines how that service becomes accessible from Windows.

**Key learning:** Container logs provide useful evidence when investigating service startup, connection failures and application behaviour.

---

## 10 — Troubleshooting a Missing MongoDB Port Mapping

One of the most useful troubleshooting experiences occurred when I realised that I had initially started the MongoDB container without publishing its port to Windows.

### The problem

MongoDB and Mongo Express were already communicating successfully over the custom Docker network.

However, my FastAPI application was running directly on Windows and needed to reach MongoDB through `localhost:27017`.

Without a published host port, that connection path was unavailable.

### Investigation

This highlighted the distinction between:

**Container-to-container communication**

```text
Mongo Express
    |
    | mongo-net
    v
chioma_mongodb:27017

```

**Host-to-container communication**

```text
FastAPI on Windows
    |
    | localhost:27017
    v
Published Docker port
    |
    v
MongoDB container:27017

```

The first connection does not require MongoDB's port to be published.

The second does, because FastAPI was not running inside the Docker network.

### Resolution

I stopped and removed the existing MongoDB container, then recreated it with the required port mapping.

```bash
docker stop chioma_mongodb
docker rm chioma_mongodb

```

The recreated container included the MongoDB port mapping.

I also learned that `docker update` does not provide a way to add a new published port mapping to an existing container.

**Important:** Removing a container can remove data stored only in its writable container filesystem. For persistent MongoDB data, Docker volumes should be configured before relying on container recreation.

This introduces a key concept explored further in the Docker volumes project.

### Implementation evidence

**Figure 6 — Page 4 — Investigation and recreation of MongoDB after identifying the missing host port mapping.**

![Investigation and recreation of MongoDB after identifying the missing host port mapping.](evidence/05-mongodb-port-troubleshooting.png)

---


## 11 — Connecting FastAPI to Containerised MongoDB

With MongoDB accessible through the published port, I configured the Python application to communicate with the database using PyMongo.

### Database configuration

The application uses a MongoDB connection URI supplied through an environment variable.

A local example is:

```env
MONGO_URI=mongodb://<mongo-admin>:<mongo-password>@localhost:27017/?authSource=admin

```

This avoids embedding real credentials directly in the Python source code.

The Python database module uses `MongoClient` to establish the connection and selects the application database and collection.

```python
import os

from pymongo import MongoClient

MONGO_URI = os.environ["MONGO_URI"]

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=3000
)

database = client["user-account"]
profiles = database["users"]

```

The project's environment configuration is loaded locally using `python-dotenv`.

### Testing connectivity

I verified the connection by sending a MongoDB ping command through the Python client.

```bash
uv run python -c "from app.database import client; print(client.admin.command('ping'))"

```

The successful response was:

```python
{'ok': 1.0}

```

This confirmed that the Python application could communicate with MongoDB running inside Docker.

### Implementation evidence

**Figure 7 — Page 5 — FastAPI database integration and terminal connectivity test against containerised MongoDB.**

![FastAPI database integration and terminal connectivity test against containerised MongoDB.](evidence/06-python-mongodb-connectivity.png)

---


## 12 — Developing Python Girls That Code

After establishing the database connection, I continued developing the application beyond the original starter form.

**Python Girls That Code** is a small profile management application built with FastAPI, MongoDB and a custom HTML/CSS/JavaScript frontend.

Its purpose is to provide a practical application that can be extended across future DevOps projects.

### Application features

- Create a new coding profile.
- Store a member's name, email, job title, biography and skills.
- Retrieve individual profiles.
- View the coding girls directory on demand.
- Update an existing member's profile.
- Delete a profile.
- Display member information through a custom frontend.

### REST API endpoints

| HTTP method | Endpoint                 | Function              |
| :---------- | :----------------------- | :-------------------- |
| `POST`      | `/profiles`              | Create a profile      |
| `GET`       | `/profiles`              | Retrieve all profiles |
| `GET`       | `/profiles/{profile_id}` | Retrieve one profile  |
| `PUT`       | `/profiles/{profile_id}` | Update a profile      |
| `DELETE`    | `/profiles/{profile_id}` | Delete a profile      |

The backend uses Pydantic models to validate incoming profile data.

MongoDB stores each member as a document in the `users` collection.

Each newly created profile receives a unique MongoDB `ObjectId`, allowing multiple users to be stored and managed independently.

### Running the application locally

With MongoDB running and the environment configured:

```bash
uv run uvicorn app.main:app --reload

```

The application is accessible at:

```text
http://127.0.0.1:8000

```

FastAPI's automatically generated API documentation is available at:

```text
http://127.0.0.1:8000/docs

```

The frontend is served by FastAPI, while its CSS and images are served through the `/static` route.

### Implementation evidence

**Figure 8 — Page 6, top — Custom Python Girls That Code profile form running in the browser.**

![Custom Python Girls That Code profile form running in the browser.](evidence/07-python-girls-frontend.png)

**Figure 9 — Page 6, bottom — The saved profile visible in Mongo Express under the `users` collection.**

![The saved profile visible in Mongo Express under the `users` collection.](evidence/08-mongodb-stored-profile.png)

---


## 13 — Building a Custom FastAPI Docker Image

The first two containers established MongoDB storage and its management interface. To complete the Docker-for-local-development demonstration, I then packaged **my own FastAPI application** into an image, rather than using the training video's Node.js application.

### Dockerfile: adapting the Node.js example to Python

The training example used a Node.js base image, `npm install` and `node server.js`. My equivalent uses a Python 3.13 base image, the `uv` dependency manager, and Uvicorn to serve FastAPI.

```dockerfile
# Base image provides the Python runtime
FROM python:3.13-slim

# Default working directory inside the image
WORKDIR /home/app

# Copy dependency manifests before application source for build caching
COPY pyproject.toml uv.lock ./

# Install uv and synchronise locked dependencies
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev --no-install-project

# Copy the application, templates and static assets
COPY ./app ./app

# Document the port served by Uvicorn
EXPOSE 8000

# Bind to all container interfaces so published-port traffic can reach FastAPI
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

*This is the Dockerfile design used in this project; refer to the committed `Dockerfile` for the exact reproducible build definition.*

The **build context** is the project root. A `.dockerignore` excludes `.venv`, `.env`, `.env.docker`, Python caches, Git metadata and other unnecessary files so that secrets and local environments do not enter the image build context.

### Build and verify the image

```bash
docker build -t python-girls-that-code:1.0 .
docker images
```

Here, `-t` assigns the repository name and version tag. The final `.` supplies the current directory as Docker's build context. I confirmed the resulting `python-girls-that-code:1.0` image in the local image list.

### Implementation evidence

**Figure 10 — Page 7 — The completed Python 3.13 / `uv` / Uvicorn Dockerfile in VS Code.**

![The completed Python 3.13 / `uv` / Uvicorn Dockerfile in VS Code.](evidence/09-fastapi-dockerfile.png)

**Figure 11 — Page 9, top — Successful Docker image build from the project root.**

![Successful Docker image build from the project root.](evidence/10-docker-build-success.png)

**Figure 12 — Page 9, bottom — The tagged `python-girls-that-code:1.0` image in `docker images`.**

![The tagged `python-girls-that-code:1.0` image in `docker images`.](evidence/11-custom-image-verification.png)

---


## 14 — Runtime Configuration & Three-Container Deployment

### Why two environment files?

Initially, FastAPI ran directly on Windows and connected to MongoDB through the host's published port:

```env
# Example only — replace placeholders locally
MONGO_URI=mongodb://<username>:<password>@127.0.0.1:27017/?authSource=admin
```

After containerising FastAPI, the database address needed to use **Docker network DNS**, not the Windows loopback interface:

```env
# .env.docker — example only; keep actual credentials out of Git
MONGO_URI=mongodb://<username>:<password>@chioma_mongodb:27017/user-account?authSource=admin
```

The `.env` and `.env.docker` files support two execution environments without modifying Python source code. Docker does **not** automatically read `.env.docker` from the Dockerfile. Instead, the file is supplied when the container is created using `--env-file`. The values become environment variables **inside the running container**, not layers embedded in the image.

### Start the FastAPI container

With MongoDB and Mongo Express already running on `mongo-net`, I started the application image using:

```bash
docker run -d \
  --name python-girls-app \
  --network mongo-net \
  -p 8000:8000 \
  --env-file .env.docker \
  python-girls-that-code:1.0
```

| Option | Why it matters |
| :-- | :-- |
| `-d` | Starts the service in detached mode |
| `--name` | Provides a stable, recognisable container name |
| `--network mongo-net` | Enables FastAPI to resolve and reach `chioma_mongodb` |
| `-p 8000:8000` | Forwards Windows host port 8000 to Uvicorn's container port 8000 |
| `--env-file .env.docker` | Injects the MongoDB URI at container creation time |
| `python-girls-that-code:1.0` | Specifies the custom image and tag to run |

### Access and verification

I accessed the containerised application from the Windows browser at **`http://localhost:8000`**. Although `localhost` refers to Windows in this browser, Docker forwards the connection to the container through the published port mapping. Mongo Express remains accessible at **`http://localhost:8081`**.

```bash
docker ps
docker logs python-girls-app
```

A useful verification exercise is to stop the locally launched Uvicorn process, confirm that the website remains available through Docker, then stop and restart the FastAPI container to observe the difference:

```bash
docker stop python-girls-app
docker start python-girls-app
```

This demonstrates that the web application is being served by the container rather than the local Python virtual environment. **The `EXPOSE 8000` Dockerfile instruction documents the container port; `-p` actually publishes it.**

### Implementation evidence

**Figure 13 — Page 10, middle — `docker ps` verifying the three services and the published FastAPI port.**

![`docker ps` verifying the three services and the published FastAPI port.](evidence/12-three-running-containers.png)

**Figure 14 — Page 10, bottom — Uvicorn startup logs confirming the FastAPI container is serving on port 8000.**

![Uvicorn startup logs confirming the FastAPI container is serving on port 8000.](evidence/13-fastapi-container-logs.png)

---




---

## 15 — Evidence Register & Screenshot Source Guide

The screenshots in this README are placed **beside the stages they verify**, not collected here as a detached gallery. Every filename below corresponds to a screenshot in my original 11-page execution walkthrough. The **source page** tells me exactly which image to crop and save. All screenshots must be sanitised before committing to GitHub.

| README figure | Screenshot to extract from execution notes | Source page | Save as |
| :-- | :-- | :--: | :-- |
| 2 | Docker Engine connection error followed by successful `docker pull mongo` | **1** | `evidence/01-docker-engine-recovery.png` |
| 3 | `docker images` showing MongoDB and Mongo Express images | **2** | `evidence/02-downloaded-docker-images.png` |
| 4 | `docker network create mongo-net` and `docker network ls` | **2** | `evidence/03-custom-docker-network.png` |
| 5 | Mongo Express interface showing `user-account` database | **3** | `evidence/04-mongo-express-database.png` |
| 6 | Terminal showing the MongoDB port-mapping investigation/recreation | **4** | `evidence/05-mongodb-port-troubleshooting.png` |
| 7 | VS Code database connection code and successful terminal test | **5** | `evidence/06-python-mongodb-connectivity.png` |
| 8 | Python Girls That Code browser application | **6 (top)** | `evidence/07-python-girls-frontend.png` |
| 9 | Mongo Express `users` collection with the saved profile | **6 (bottom)** | `evidence/08-mongodb-stored-profile.png` |
| 10 | VS Code displaying the completed Dockerfile | **7** | `evidence/09-fastapi-dockerfile.png` |
| 11 | Successful `docker build` output | **9 (top)** | `evidence/10-docker-build-success.png` |
| 12 | `docker images` showing `python-girls-that-code:1.0` | **9 (bottom)** | `evidence/11-custom-image-verification.png` |
| 13 | `docker ps` showing the FastAPI, MongoDB and Mongo Express containers | **10 (middle)** | `evidence/12-three-running-containers.png` |
| 14 | `docker logs` showing Uvicorn listening on `0.0.0.0:8000` | **10 (bottom)** | `evidence/13-fastapi-container-logs.png` |

**Page 8 is intentionally excluded from the screenshot list:** it displays a database connection URI containing a password. The environment-file design is explained in Section 14 using redacted examples instead. If I want an environment-configuration screenshot later, I will capture a fresh one with **all credentials replaced by placeholders**.

The final architecture image is **not** an existing screenshot in the walkthrough; it is a separate diagram to create and save as `architecture/docker-local-development-workflow.png` (Figure 1).

**Evidence limitations:** The browser screenshot on page 6 demonstrates the application running and saving a profile during local development; it does **not by itself prove** that the frontend was served from the FastAPI container. The final `docker ps` and Uvicorn log screenshots on page 10 verify container execution. A fresh browser screenshot taken while local Uvicorn is stopped would provide even stronger final end-to-end evidence.

---

## 16 — Challenges, Troubleshooting & Lessons Learned

| Challenge                                     | Investigation / Resolution                                          | Learning outcome                                                           |
| :-------------------------------------------- | :------------------------------------------------------------------ | :------------------------------------------------------------------------- |
| Docker CLI could not connect to Docker Engine | Started Docker Desktop and its Linux backend                        | Docker CLI and Docker Engine have distinct responsibilities                |
| Python interpreter incompatibility            | Pinned Python 3.13 and recreated the virtual environment            | Python version requirements affect dependency management                   |
| Understanding Docker networking               | Created a user-defined bridge network for MongoDB and Mongo Express | Containers can communicate through internal networking and name resolution |
| Missing MongoDB port publication              | Recreated MongoDB container with the required host port mapping     | Host-to-container and container-to-container networking are different      |
| Connecting Python to MongoDB                  | Configured PyMongo with a MongoDB URI and tested connectivity       | Applications use database clients and connection strings                   |
| Avoiding hardcoded credentials                | Moved connection configuration into environment variables           | Configuration should be separated from application source code             |
| Managing multiple profiles                    | Introduced MongoDB ObjectIds and REST CRUD endpoints                | Database documents can be identified and updated independently             |
| Dockerising the Python application | Adapted a Node.js Dockerfile to Python, uv and Uvicorn | The application runtime and dependency installation must match the chosen language |
| Hostname changed after containerisation | Used `chioma_mongodb` rather than `localhost` inside FastAPI container | Loopback addresses are scoped to each container or host |
| Preventing secrets in images | Added `.dockerignore` and injected configuration with `--env-file` | Build-time packaging and runtime configuration are separate concerns |

### Additional technical insights

**Docker images versus containers:** Images are reusable packages, while containers are running or stopped instances created from images.

**Detached mode:** The `-d` flag allows containers to run without occupying the terminal session.

**Container naming:** Explicit container names improve readability and support network-based service discovery.

**MongoDB collections:** MongoDB does not require a rigid schema to be declared before inserting documents. However, the FastAPI application uses Pydantic models to validate the data it accepts.

**Environment variables:** They make application configuration more flexible, although additional secret-management controls are required in production environments.

**Git commits:** The application was developed incrementally, with commits documenting meaningful changes rather than treating the entire implementation as a single final upload.

---

## 17 — Security & Development Considerations

This project is designed as a local development and learning environment.

The following practices are important when adapting it for production:

- Never commit `.env` files or real database credentials.
- Use strong, unique passwords and appropriate database permissions.
- Avoid exposing MongoDB directly to untrusted networks.
- Prefer binding local development ports to `127.0.0.1`.
- Use Docker secrets or an appropriate secrets manager where applicable.
- Configure persistent storage for MongoDB.
- Add user authentication and authorisation before exposing profile management endpoints publicly.
- Use HTTPS for publicly accessible services.
- Avoid placing database passwords directly in shell commands in shared or production environments.

The current application demonstrates CRUD operations but does not yet implement user authentication or per-user access control.

---

## 18 — Future Improvements

This application is intended to evolve as I progress through the DevOps bootcamp.

Planned improvements include:

- Using Docker Compose to manage multiple services together.
- Configuring Docker volumes for persistent MongoDB storage.
- Publishing application images to a private Docker registry.
- Deploying the application to a remote server.
- Introducing CI/CD automation.
- Adding user authentication and access controls.
- Supporting profile picture uploads.
- Expanding application observability and monitoring.

These enhancements will be documented in subsequent projects as the relevant concepts are introduced and implemented.

---

## 19 — Project Reflection

This project marked an important change in my approach to hands-on DevOps learning. It began with a simple Python application and progressed through Docker Engine troubleshooting, a shared container network, database connectivity, a custom application image and a working three-container environment.

Rather than repeatedly cloning the sample application used in the training demonstrations, I chose to develop and maintain my own Python application while following the same underlying infrastructure concepts.

This introduced additional troubleshooting opportunities, from Python version management to Docker Engine connectivity, networking and database integration.

The experience reinforced that DevOps engineering involves understanding how applications, runtime environments, networking, databases and deployment tooling interact. The transition from a host-run FastAPI service to a containerised service made the distinction between **host networking, container networking and runtime configuration** particularly concrete.

Most importantly, building an application I understand and can continue developing makes each new infrastructure concept more meaningful.

**The goal is not simply to execute Docker commands successfully, but to understand what each command does, why it is needed, and how it supports a working application.**

---

## 20 — Portfolio Navigation

**Project:** Dev7a — Docker for Local Development

**Module:** 7 — Containers with Docker

**Application:** Python Girls That Code

**Portfolio:** [DevOps Engineering Portfolio](https://github.com/ChiomaScripts/DevOps-Portfolio)

**Previous projects:**

- [Dev5 — Cloud Infrastructure & Java Application Deployment](https://github.com/ChiomaScripts/Dev5-cloud-iaas)
- [Dev6 — Nexus Artifact Repository Management](https://github.com/ChiomaScripts/Dev6-nexus-artifact-repository)

---

*Built through hands-on experimentation, troubleshooting and continuous learning.*
