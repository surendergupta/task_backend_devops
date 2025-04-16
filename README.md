# Projects for Devops cloud backend engineer

## 🌐 Task 1: Deploy a Self-hosted n8n Instance on Google Cloud Free Tier
- **Objective:** Deploy a secure and persistent n8n instance on a GCP E2-micro VM, using Docker Compose, accessible via browser with authentication and firewall security.
- **Requirement:** 
    - Google Cloud Platform account
    - GCP project with billing enabled
    - SSH access (via browser or SSH key)

### Create GCP VM (E2-Micro)
- Go to Google Cloud Console → Compute Engine → VM Instances.
- Click "Create Instance".
    - Name: n8n-instance
    - Region: us-central1
    - Zone: us-central1-a
    - Machine type: e2-micro
    - OS: Ubuntu
    - Version: 22.04 LTS
    - Firewall: Allowed Port
        - HTTP and HTTPS Traffic
        - SSH
        - 5678
    - Authentication: SSH KEY
- Click Create

### SSH into VM (After VM Provision Access)
- Wait till GCP VM IN Ready State
- Goto top right click on Cloud Shell Terminal
- Goto VM connect -> view gcloud Command
```
gcloud compute ssh --zone "us-central1-a" "n8n-instance" --project "syllabustracker-456512"
```
- The Above Command paste in Cloud Shell Terminal and login into VM

### Install Docker & Docker Compose (After Login into VM)
- Update and install some package of docker and docker compose
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
docker ps
docker --version

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version

```

### Setup n8n
- Create a directory for n8n:
```
mkdir ~/n8n && cd ~/n8n
```
- Create a .env file:`vi .env`
- Copy below Variable and paste into `.env` file
```
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin@123
N8N_HOST=35.225.123.1
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_SECURE_COOKIE=false
```
- Create a `docker-compose.yml` file: `vi docker-compose.yml`
- Copy below content into `docker-compose.yml` file
```
version: "3"
services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=${N8N_BASIC_AUTH_ACTIVE}
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=${N8N_PORT}
      - N8N_PROTOCOL=${N8N_PROTOCOL}
      - N8N_SECURE_COOKIE=${N8N_SECURE_COOKIE}
    volumes:
      - n8n_data:/home/node/.n8n
volumes:
  n8n_data:
```
- Start n8n:
```
docker-compose up -d
```
- View container running in Docker use command
```
docker ps
```

### Access URL
- Open http://<external-ip>:5678 in your browser. `http://35.225.123.1:5678`
- Login using your configured basic auth credentials.

### Secure the VM
- **Firewall:** Ensure only ports 22 (SSH) and 5678 (n8n) are open.
- **SSH Keys:** Use key-based SSH only (no password login). `sudo nano /etc/ssh/sshd_config`
```
PermitRootLogin no
PasswordAuthentication no
```
- After Save file restart ssh
```
sudo systemctl restart ssh
```

### Clean UP 
```
docker-compose down
cd ..
rm -rf ~/n8n
```

### Automate Deployment
- Create `n8n-deploy-gcp.sh` file: `vi n8n-deploy-gcp.sh`
- Copy below content into `n8n-deploy-gcp.sh` file
```bash
#!/bin/bash

# Install dependencies and curl
sudo apt update && sudo apt install -y curl

# Install Docker
sudo apt install -y docker.io

# Docker Compose install
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create n8n folder
mkdir ~/n8n && cd ~/n8n

# Write .env
cat <<EOF > .env
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin@123
N8N_HOST=$(curl ifconfig.me)
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_SECURE_COOKIE=false
EOF

# Write docker-compose.yml
cat <<EOF > docker-compose.yml
version: "3"
services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=\${N8N_BASIC_AUTH_ACTIVE}
      - N8N_BASIC_AUTH_USER=\${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=\${N8N_BASIC_AUTH_PASSWORD}
      - N8N_HOST=\${N8N_HOST}
      - N8N_PORT=\${N8N_PORT}
      - N8N_PROTOCOL=\${N8N_PROTOCOL}
      - N8N_SECURE_COOKIE=\${N8N_SECURE_COOKIE}
    volumes:
      - n8n_data:/home/node/.n8n
volumes:
  n8n_data:
EOF

# Start n8n
docker-compose up -d

```

- Execute Bash Script and deploy n8n
```bash 
chmod +x n8n-deploy-gcp.sh
./n8n-deploy-gcp.sh

```

### Final Output for Submission
```yaml
URL: http://35.225.123.1:5678
Username: admin
Password: admin@123
Persistent Volume: Docker volume (n8n_data)
Secured SSH: Yes (SSH Key + No root login)
```

## 🌐 Task 2: Containerize & Deploy a Sample FastAPI Agent Backend

## Create Sample Fast API
- Create Folder `Sample-api`
- Create `main.py` file
```python
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
import os
import uvicorn

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.ai_safety_log_api_db
collection = db.incidents

# Pydantic Models
class IncidentBase(BaseModel):
    title: str
    description: str
    severity: str
    reported_at: datetime = datetime.utcnow()

class IncidentData(IncidentBase):
    id: str

class IncidentResponse(BaseModel):
    status_code: int
    message: str
    data: IncidentData | None = None

class IncidentListResponse(BaseModel):
    status_code: int
    message: str
    data: list[IncidentData]

# Utility function to convert MongoDB document
async def serialize_incident(document) -> IncidentData:
    return IncidentData(
        id = str(document["_id"]), 
        title=document["title"],
        description=document["description"],
        severity=document["severity"],
        reported_at=document["reported_at"]
    )

# API Endpoints
@app.get("/", response_model=dict)
async def index():
    return {"message": "Welcome to the AI Safety Log API"}

# GET /incidents - Retrieve all incidents
@app.get("/incidents", response_model=IncidentListResponse)
async def get_incidents():
    incidents = await collection.find().to_list(25)
    
    return IncidentListResponse(
        status_code=200,
        message="All Incidents retrieved",
        data=[await serialize_incident(doc) for doc in incidents]
    )


# POST /incidents - Create a new incident
@app.post("/incidents", response_model=IncidentResponse)
async def create_incident(incident: IncidentBase):
    if incident.severity not in ["Low", "Medium", "High"]:
        raise HTTPException(status_code=400, detail="Invalid severity level")
    new_incident = await collection.insert_one(incident.dict())
    created_incident = await collection.find_one({"_id": new_incident.inserted_id})
    return IncidentResponse(
        status_code=201,
        message="Incident successfully created",
        data=await serialize_incident(created_incident)
    )
    

# GET /incidents/{id} - Retrieve a specific incident
@app.get("/incidents/{id}", response_model=IncidentResponse)
async def get_incident(id: str):
    incident = await collection.find_one({"_id": ObjectId(id)})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    return IncidentResponse(
        status_code=200,
        message="Incident successfully retrieved",
        data=await serialize_incident(incident)
    )

# DELETE /incidents/{id} - Delete an incident
@app.delete("/incidents/{id}", response_model=IncidentResponse)
async def delete_incident(id: str):
    result = await collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse(
        status_code=200,
        message="Incident successfully deleted",
        data=None
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
- Create `requirements.txt` file
```txt
fastapi
uvicorn
motor
pydantic
python-dotenv
```
- Create `.env` file
```bash
MONGO_URI=mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER_NAME>.zzrkght.mongodb.net/
```
- Create Dockerfile
```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

```


### For Local Setup and Test

- Create virtual env for local Development Setup
```bash
python -m venv fastapi-env
```
- Activate 
```bash
.\fastapi-env\Scripts\activate
```
- Install Dependencies
```
pip install -r requirements.txt
```
- Run API
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Build Local & Run inside a container
```bash
docker build -t fastapi-agent .
docker run -d -p 8000:8000 -e "MONGO_URI=mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER_NAME>.zzrkght.mongodb.net/" fastapi-agent
```

### Local Test Output for Submission
```yaml
URL: http://localhost:8000
DOCS: http://localhost:8000/docs
REDOC: http://localhost:8000/redoc
```

### Push to Google Artifacts Registry
```
docker tag fastapi-agent us-central1-docker.pkg.dev/syllabustracker-456512/fastapi-repo/fastapi-agent
```

### Install Google cloud CLI
- Install Cli form url below. Select your Operating System and Architecture
```
https://cloud.google.com/sdk/docs/install
```
- In Window Follow instruction and Install
- Authenticate your account `You must sign in to continue. Would you like to sign in (Y/n)?  y` show url and click on url and follow instructions
- After Authenticate `You are signed in as: [gupta.surender.1990@gmail.com].`
- Pick cloud project to use: Select your Project `Please enter numeric choice or text value (must exactly match list item):  17`
- Your current project has been set to: [syllabustracker-456512].
- Next `Do you want to configure a default Compute Region and Zone? (Y/n)?  y`
- Which Google Compute Engine zone would you like to use as project default? `Please enter numeric choice or text value (must exactly match list item):  8`
- Your project default Compute Engine zone has been set to [us-central1-a].
```bash
gcloud auth login --no-launch-browser
```
- You are now logged in as [gupta.surender.1990@gmail.com].
```bash 
gcloud config set project syllabustracker-456512
gcloud projects get-iam-policy syllabustracker-456512
gcloud projects add-iam-policy-binding syllabustracker-456512 --member="user:gupta.surender.1990@gmail.com" --role="roles/artifactregistry.writer"
gcloud auth configure-docker us-central1-docker.pkg.dev
gcloud services enable artifactregistry.googleapis.com
```
- If required relogin
```bash
gcloud auth application-default login
```
- Show like this
```output
Credentials saved to file: [C:\Users\PriyaJi\AppData\Roaming\gcloud\application_default_credentials.json]

These credentials will be used by any library that requests Application Default Credentials (ADC).

Quota project "syllabustracker-456512" was added to ADC which can be used by Google client libraries for billing and quota. Note that some services may still bill the project owning the resource.
```
- Push to Artifact Registry
```bash
docker push us-central1-docker.pkg.dev/syllabustracker-456512/fastapi-repo/fastapi-agent
```
- Output in console 
```
Using default tag: latest
The push refers to repository [us-central1-docker.pkg.dev/syllabustracker-456512/fastapi-repo/fastapi-agent]
2a47a8c4fd5c: Pushed
c79e33b818ec: Pushed
b13f6ff7acb7: Pushed
9c538fc35491: Pushed
47bbb0afa7fe: Pushed
e705847bb5b6: Pushed
9679266ce23b: Pushed
f10bf87e184c: Pushed
8a628cdd7ccc: Pushed
latest: digest: sha256:11b4cdf3b75ed77f833b51312c2dffd6d18e227ee9da6bebfc134515722d78e3 size: 856
```

### Deploy to Cloud Run
- Update IAM Policy
```bash
gcloud projects add-iam-policy-binding syllabustracker-456512 --member="user:gupta.surender.1990@gmail.com" --role="roles/run.admin"
```
- Update IAM Policy role
```bash
gcloud projects add-iam-policy-binding syllabustracker-456512 --member="user:gupta.surender.1990@gmail.com" --role="roles/iam.serviceAccountUser"
```
- Deploy without env variable
```bash
gcloud run deploy fastapi-agent --image=us-central1-docker.pkg.dev/syllabustracker-456512/fastapi-repo/fastapi-agent --platform=managed --region=us-central1 --allow-unauthenticated --port=8000
```
- Deploy with env variable
```bash
gcloud run deploy fastapi-agent --image=us-central1-docker.pkg.dev/syllabustracker-456512/fastapi-repo/fastapi-agent --platform=managed --region=us-central1 --allow-unauthenticated --port=8000 --set-env-vars=MONGO_URI="mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER_NAME>.zzrkght.mongodb.net/"
```

### Output for Submission

```txt
Deploying container to Cloud Run service [fastapi-agent] in project [syllabustracker-456512] region [us-central1]
OK Deploying... Done.
  OK Creating Revision...
  OK Routing traffic...
  OK Setting IAM Policy...
Done.
Service [fastapi-agent] revision [fastapi-agent-00002-8v8] has been deployed and is serving 100 percent of traffic.
Service URL: https://fastapi-agent-154172965587.us-central1.run.app
```

### Clean Up
```bash
gcloud run services delete fastapi-agent --platform=managed --region=us-central1
gcloud artifacts docker images delete us-central1-docker.pkg.dev/syllabustracker-456512/fastapi-repo/fastapi-agent:latest --delete-tags
```

### GitAction deployment
- Create a file `.github/workflows/deploy.yml`
- Copy below content into `.github/workflows/deploy.yml` file
```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Google Cloud
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Configure Docker
        run: gcloud auth configure-docker us-central1-docker.pkg.dev
      
      - name: Build Docker image
        run: |
          docker build -t us-central1-docker.pkg.dev/syllabustracker-456512/fastapi-repo/fastapi-agent ./sample-api

      - name: Push to Artifact Registry
        run: |
          docker push us-central1-docker.pkg.dev/syllabustracker-456512/fastapi-repo/fastapi-agent

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy fastapi-agent \
            --image=us-central1-docker.pkg.dev/syllabustracker-456512/fastapi-repo/fastapi-agent \
            --platform=managed \
            --region=us-central1 \
            --allow-unauthenticated \
            --port=8000 \
            --set-env-vars=MONGO_URI="mongodb+srv://<USERNAME>:<PASSWORD>@<CLUSTER_NAME>.zzrkght.mongodb.net/"
```
### Github Action Output for Submission
```txt
Deploying container to Cloud Run service [fastapi-agent] in project [syllabustracker-456512] region [us-central1]
Deploying...
Setting IAM Policy.............done
Creating Revision.................................................................................................................................done
Routing traffic.....done
Done.
Service [fastapi-agent] revision [fastapi-agent-00003-gbt] has been deployed and is serving 100 percent of traffic.
Service URL: https://fastapi-agent-154172965587.us-central1.run.app
```

### If Find Issue on IAM Permission or Repositry not found
- Create IAM Service Account and add Policy on it.
```bash
gcloud iam service-accounts create github-deployer --description="Service account for GitHub Actions deployments" --display-name="GitHub Deployer"
gcloud projects add-iam-policy-binding syllabustracker-456512 --member="serviceAccount:github-deployer@syllabustracker-456512.iam.gserviceaccount.com" --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding syllabustracker-456512  --member="serviceAccount:github-deployer@syllabustracker-456512.iam.gserviceaccount.com" --role="roles/run.admin"
gcloud projects add-iam-policy-binding syllabustracker-456512 --member="serviceAccount:github-deployer@syllabustracker-456512.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"
```
- Create a Key file to deploy
```bash
gcloud iam service-accounts keys create key.json --iam-account=github-deployer@syllabustracker-456512.iam.gserviceaccount.com
```
- Github Secret add this key.json file data
- Create a artifact repository
```bash
gcloud artifacts repositories create fastapi-repo --repository-format=docker --location=us-central1
```

### Final Output for Submission
```yaml
URL: https://fastapi-agent-154172965587.us-central1.run.app
DOCS: https://fastapi-agent-154172965587.us-central1.run.app/docs
REDOC: https://fastapi-agent-154172965587.us-central1.run.app/redoc
```

### Screenshot Both Task 1

![alt text](<screenshots/Screenshot 2025-04-16 141224.png>)

![alt text](<screenshots/Screenshot 2025-04-16 142128.png>)
![alt text](<screenshots/Screenshot 2025-04-16 142141.png>)
![alt text](<screenshots/Screenshot 2025-04-16 142240.png>)
![alt text](<screenshots/Screenshot 2025-04-16 143139.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 143407.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 144450.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 144940.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 150015.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 150549.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 160039.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 163319.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 163421.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 163752.png>) 

### Screenshot Both Task 2

![alt text](<screenshots/Screenshot 2025-04-16 171748.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 171800.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 171812.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 172418.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 172724.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 172802.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 173137.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 180150.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 180207.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 181206.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 181734.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 181751.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 181805.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 185440.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 235915.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 235934.png>) 
![alt text](<screenshots/Screenshot 2025-04-16 235951.png>) 
![alt text](<screenshots/Screenshot 2025-04-17 000025.png>) 
![alt text](<screenshots/Screenshot 2025-04-17 000100.png>) 
![alt text](<screenshots/Screenshot 2025-04-17 000213.png>) 
![alt text](<screenshots/Screenshot 2025-04-17 000232.png>)