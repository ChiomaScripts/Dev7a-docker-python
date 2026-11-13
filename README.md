# Dev7a — Docker for Local Development | Python, FastAPI & MongoDB

**Container Networking, Docker Desktop, MongoDB Integration & Application Development**

Part of my hands-on DevOps engineering portfolio, documenting my progression through containerisation, application deployment, infrastructure automation and cloud technologies.

**Module 7 — Containers with Docker**

---

## 01 — Project Overview

This project explores how Docker can be used to establish a local development environment where an application communicates with a database running inside a container.

The original training demonstration uses a Node.js application alongside MongoDB and Mongo Express. I chose to adapt the implementation using **Python and FastAPI**, building my own application rather than relying entirely on the provided JavaScript source code.

This allowed me to combine my existing Python knowledge with new Docker concepts while gaining practical experience in application development, database integration, container networking and troubleshooting.

The application, **Python Girls That Code**, is a profile management platform where coding enthusiasts can create and manage their profiles, including their names, email addresses, job titles, biographies and technical skills.

The application uses FastAPI for its backend, MongoDB for data storage and Mongo Express for database administration.

### Project objectives

- Understand how Docker CLI, Docker Engine and Docker Desktop work together.
- Pull and manage container images from Docker Hub.
- Create and configure Docker containers using command-line arguments.
- Establish communication between containers using a custom Docker network.
- Configure MongoDB authentication using environment variables.
- Publish container ports to make services accessible from the Windows host.
- Connect a locally running Python/FastAPI application to containerised MongoDB.
- Verify database connectivity and perform application-level CRUD operations.
- Troubleshoot Docker networking, service availability and configuration issues.

### Technologies used

| Technology | Purpose |
|---|---|
| Docker | Container management and local development |
| Docker Desktop | Docker Engine integration on Windows |
| WSL 2 / Linux backend | Linux environment for Docker containers |
| Python 3.13 | Application programming language |
| FastAPI | Backend API framework |
| Uvicorn | ASGI application server |
| MongoDB | NoSQL document database |
| Mongo Express | Web-based MongoDB administration |
| PyMongo | Python MongoDB client |
| uv | Python project and dependency management |
| HTML, CSS, JavaScript | Application frontend |
| Git & GitHub | Version control and project documentation |
| VS Code | Development environment |

---

## 02 — Application Architecture

The local development environment consists of a Python application running on Windows and two Docker containers communicating through a shared Docker network.

```text
                WINDOWS DEVELOPMENT HOST
┌────────────────────────────────────────────────┐
│                                                │
│  Browser                                       │
│     │                                          │
│     ├──── localhost:8000                       │
│     │          │                               │
│     │          ▼                               │
│     │    Python / FastAPI                      │
│     │    Girls That Code                       │
│     │          │                               │
│     │          │ PyMongo                       │
│     │          │ localhost:27017               │
│     │          ▼                               │
│     │    Published MongoDB Port                │
│     │          │                               │
│     └──── localhost:8081                       │
│                │                               │
│                ▼                               │
│          Mongo Express UI                      │
│                                                │
└────────────────────────────────────────────────┘
                 │
                 ▼
             DOCKER ENGINE
┌────────────────────────────────────────────────┐
│                                                │
│              mongo-net                         │
│         Custom Docker Network                  │
│                                                │
│   ┌──────────────────────┐                     │
│   │ MongoDB Container    │◄─────────┐          │
│   │ chioma_mongodb       │          │          │
│   │ Port 27017           │          │          │
│   └──────────────────────┘          │          │
│                                     │          │
│   ┌──────────────────────┐          │          │
│   │ Mongo Express        │──────────┘          │
│   │ chioma_mongoexp      │                     │
│   │ Port 8081            │                     │
│   └──────────────────────┘                     │
│                                                │
└────────────────────────────────────────────────┘
```

### Understanding the connections

There are two distinct communication paths in this implementation.

**1. Container-to-container communication**

Mongo Express communicates directly with MongoDB using the MongoDB container's name and internal port:

`chioma_mongodb:27017`

Because both containers belong to the same user-defined Docker network, Docker provides name resolution that allows Mongo Express to locate MongoDB without requiring MongoDB's port to be published to Windows.

**2. Host-to-container communication**

The FastAPI application runs directly on Windows rather than inside the Docker network.

To access MongoDB, it connects through the host's published MongoDB port:

`localhost:27017`

Docker forwards this connection to port `27017` inside the MongoDB container.

This distinction was one of the most important networking concepts I learned during the project.

---

## 03 — Preparing the Python Application

Rather than cloning the Node.js application from the training demonstration, I developed a Python-based alternative using FastAPI.

The project was initialised using `uv`, with FastAPI, Uvicorn and PyMongo installed as application dependencies.

```bash
uv init --bare
uv add fastapi uvicorn pymongo
```

The `--bare` option allowed me to initialise the Python project without generating the default starter application structure, giving me more control over how the project was organised.

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

This introduced me to Python interpreter pinning, project-level Python requirements, virtual environments and dependency resolution using `uv`.

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
├── .env                  # Local only; not committed
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

The application separates API logic, database configuration, frontend templates and static assets.

The `.env` file contains local configuration and is excluded from Git to prevent credentials from being committed.

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

| Component | Responsibility |
|---|---|
| Docker CLI | Accepts commands such as `docker pull`, `docker run` and `docker ps` |
| Docker Engine | Manages images, containers, networks and other Docker resources |
| Docker Desktop | Provides the Windows application and manages its Docker environment |
| WSL 2 backend | Supplies a Linux environment for running Linux containers when selected |

Linux containers depend on Linux kernel functionality, including namespaces and cgroups.

Docker Desktop makes this possible on Windows by running a Linux backend, commonly using WSL 2.

### Resolution

After starting Docker Desktop and allowing its engine to initialise, I repeated the command.

```bash
docker pull mongo
```

The MongoDB image download proceeded successfully.

**Key learning:** Installing the Docker CLI does not necessarily mean that a running Docker Engine is available to execute commands.

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

An important distinction is that **an image is not the same as a running container**.

An image is the packaged filesystem and configuration used to create containers. A container is an instance created from that image.

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

Docker resolves `chioma_mongodb` to the MongoDB container's internal network address.

This avoids relying on container IP addresses that may change when containers are recreated.

### Internal communication versus published ports

Containers connected to the same user-defined bridge network can communicate through their internal ports without those ports being published to the host.

Publishing a port serves a different purpose: it allows a connection originating outside that Docker network, such as one from a Windows application, to reach the container.

This became especially relevant when connecting my locally running FastAPI application to MongoDB.

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

| Argument | Purpose |
|---|---|
| `docker run` | Creates and starts a container from an image |
| `-d` | Runs the container in detached mode |
| `-e` | Supplies an environment variable |
| `--name` | Assigns a recognisable container name |
| `--net` | Connects the container to a specified Docker network |
| `-p` | Publishes a container port to the host |
| `mongo` | Specifies the Docker image |

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

Binding to `127.0.0.1` limits the published port to local access, which is preferable for this development environment.

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

- `mongodb://` — MongoDB connection protocol.
- `username:password` — database authentication credentials.
- `hostname` — the MongoDB container name, `chioma_mongodb`.
- `27017` — MongoDB's default listening port.
- `authSource=admin` — specifies the authentication database for the root account.

The Mongo Express Basic Authentication credentials are separate from the credentials used to authenticate with MongoDB.

### Accessing Mongo Express

With port 8081 published, the web interface was accessible from the Windows browser at:

```text
http://localhost:8081
```

I used Mongo Express to create and inspect the application's database and `users` collection.

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

Here, `0.0.0.0` indicates that the application is listening on all available network interfaces inside its container.

The Docker port mapping determines how that service becomes accessible from Windows.

**Key learning:** Container logs provide useful evidence when investigating service startup, connection failures and application behaviour.

---

## 10 — Troubleshooting a Missing MongoDB Port Mapping

One of the most useful troubleshooting experiences occurred when I realised that I had initially started the MongoDB container without publishing its port to Windows.

### The problem

MongoDB and Mongo Express were already communicating successfully over the custom Docker network.

However, my FastAPI application was running directly on Windows and needed to reach MongoDB through `localhost:27017`.

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

I also learned that `docker update` does not provide a way to add a new published port mapping to an existing container.

**Important:** Removing a container can remove data stored only in its writable container filesystem. For persistent MongoDB data, Docker volumes should be configured before relying on container recreation.

This introduces a key concept explored further in the Docker volumes project.

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

The Python database module uses `MongoClient` to establish the connection and selects the application database and collection.

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

The project's environment configuration is loaded locally using `python-dotenv`.

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

---

## 12 — Developing Python Girls That Code

After establishing the database connection, I continued developing the application beyond the original starter form.

**Python Girls That Code** is a small profile management application built with FastAPI, MongoDB and a custom HTML/CSS/JavaScript frontend.

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

| HTTP method | Endpoint | Function |
|---|---|---|
| `POST` | `/profiles` | Create a profile |
| `GET` | `/profiles` | Retrieve all profiles |
| `GET` | `/profiles/{profile_id}` | Retrieve one profile |
| `PUT` | `/profiles/{profile_id}` | Update a profile |
| `DELETE` | `/profiles/{profile_id}` | Delete a profile |

The backend uses Pydantic models to validate incoming profile data.

MongoDB stores each member as a document in the `users` collection.

Each newly created profile receives a unique MongoDB `ObjectId`, allowing multiple users to be stored and managed independently.

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

The frontend is served by FastAPI, while its CSS and images are served through the `/static` route.

---

## 13 — Evidence of Implementation

The following screenshots document the practical implementation and verification of the project.

Screenshots should be stored in the repository's `evidence/` directory.

### Docker image retrieval

Evidence of the MongoDB and Mongo Express images downloaded from Docker Hub.

`evidence/01-docker-images.png`

### Docker networking and running containers

Evidence of the custom network and running MongoDB/Mongo Express containers.

`evidence/02-running-containers.png`

### Mongo Express

Evidence of the Mongo Express interface, application database and collection.

`evidence/03-mongo-express.png`

### Python-to-MongoDB connectivity

Evidence of the successful PyMongo ping response.

`evidence/04-mongodb-connection.png`

### Python Girls That Code

Evidence of the application's frontend and working profile management functionality.

`evidence/05-python-girls-that-code.png`

### MongoDB documents

Evidence that application profiles were successfully persisted as MongoDB documents.

`evidence/06-mongodb-profiles.png`

> Screenshot filenames are proposed documentation conventions. Add the actual screenshots and update the paths to match the files committed to the repository.

---

## 14 — Challenges, Troubleshooting & Lessons Learned

| Challenge | Investigation / Resolution | Learning outcome |
|---|---|---|
| Docker CLI could not connect to Docker Engine | Started Docker Desktop and its Linux backend | Docker CLI and Docker Engine have distinct responsibilities |
| Python interpreter incompatibility | Pinned Python 3.13 and recreated the virtual environment | Python version requirements affect dependency management |
| Understanding Docker networking | Created a user-defined bridge network for MongoDB and Mongo Express | Containers can communicate through internal networking and name resolution |
| Missing MongoDB port publication | Recreated MongoDB container with the required host port mapping | Host-to-container and container-to-container networking are different |
| Connecting Python to MongoDB | Configured PyMongo with a MongoDB URI and tested connectivity | Applications use database clients and connection strings |
| Avoiding hardcoded credentials | Moved connection configuration into environment variables | Configuration should be separated from application source code |
| Managing multiple profiles | Introduced MongoDB ObjectIds and REST CRUD endpoints | Database documents can be identified and updated independently |

### Additional technical insights

**Docker images versus containers:** Images are reusable packages, while containers are running or stopped instances created from images.

**Detached mode:** The `-d` flag allows containers to run without occupying the terminal session.

**Container naming:** Explicit container names improve readability and support network-based service discovery.

**MongoDB collections:** MongoDB does not require a rigid schema to be declared before inserting documents. However, the FastAPI application uses Pydantic models to validate the data it accepts.

**Environment variables:** They make application configuration more flexible, although additional secret-management controls are required in production environments.

**Git commits:** The application was developed incrementally, with commits documenting meaningful changes rather than treating the entire implementation as a single final upload.

---

## 15 — Security & Development Considerations

This project is designed as a local development and learning environment.

The following practices are important when adapting it for production:

- Never commit `.env` files or real database credentials.
- Use strong, unique passwords and appropriate database permissions.
- Avoid exposing MongoDB directly to untrusted networks.
- Prefer binding local development ports to `127.0.0.1`.
- Use Docker secrets or an appropriate secrets manager where applicable.
- Configure persistent storage for MongoDB.
- Add user authentication and authorisation before exposing profile management endpoints publicly.
- Use HTTPS for publicly accessible services.
- Avoid placing database passwords directly in shell commands in shared or production environments.

The current application demonstrates CRUD operations but does not yet implement user authentication or per-user access control.

---

## 16 — Future Improvements

This application is intended to evolve as I progress through the DevOps bootcamp.

Planned improvements include:

- Building a Docker image for the FastAPI application.
- Running the FastAPI application as a container.
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

## 17 — Project Reflection

This project marked an important change in my approach to hands-on DevOps learning.

Rather than repeatedly cloning the sample application used in the training demonstrations, I chose to develop and maintain my own Python application while following the same underlying infrastructure concepts.

This introduced additional troubleshooting opportunities, from Python version management to Docker Engine connectivity, networking and database integration.

The experience reinforced that DevOps engineering involves understanding how applications, runtime environments, networking, databases and deployment tooling interact.

Most importantly, building an application I understand and can continue developing makes each new infrastructure concept more meaningful.

**The goal is not simply to execute Docker commands successfully, but to understand what each command does, why it is needed, and how it supports a working application.**

---

## 18 — Portfolio Navigation

**Project:** Dev7a — Docker for Local Development

**Module:** 7 — Containers with Docker

**Application:** Python Girls That Code

**Portfolio:** [DevOps Engineering Portfolio](https://github.com/ChiomaScripts/DevOps-Portfolio)

**Previous projects:**

- [Dev5 — Cloud Infrastructure & Java Application Deployment](https://github.com/ChiomaScripts/Dev5-cloud-iaas)
- [Dev6 — Nexus Artifact Repository Management](https://github.com/ChiomaScripts/Dev6-nexus-artifact-repository)

---

*Built through hands-on experimentation, troubleshooting and continuous learning.*