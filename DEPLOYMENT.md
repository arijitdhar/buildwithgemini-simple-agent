# Deploying GlobeTrotter AI to a New Google Cloud Account

This guide explains how to deploy **GlobeTrotter AI** from this GitHub repository to a fresh Google Cloud Platform (GCP) project or account.

---

## 📋 Prerequisites & Tools

Ensure you have the following installed on your machine:
* Python 3.11+
* [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager (`pip install uv`)
* [Google Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install)
* Google Agent Development Kit CLI (`google-agents-cli`):
  ```bash
  uv tool install google-agents-cli
  ```

---

## ☁️ Step 1: Set Up Your Google Cloud Project

1. **Authenticate `gcloud` with your personal Google account**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Set your GCP project ID**:
   ```bash
   gcloud config set project YOUR_NEW_PROJECT_ID
   ```

3. **Enable required Google Cloud APIs**:
   ```bash
   gcloud services enable \
     aiplatform.googleapis.com \
     firestore.googleapis.com \
     storage.googleapis.com \
     cloudbuild.googleapis.com \
     secretmanager.googleapis.com \
     run.googleapis.com
   ```

4. **Initialize Firestore Database (Native Mode)**:
   ```bash
   gcloud firestore databases create --location=us-east1
   ```

5. **Create a public Google Cloud Storage Bucket for media assets**:
   ```bash
   gcloud storage buckets create gs://YOUR_UNIQUE_BUCKET_NAME --location=us-east1
   gcloud storage buckets add-iam-policy-binding gs://YOUR_UNIQUE_BUCKET_NAME \
     --member=allUsers --role=roles/storage.objectViewer
   ```

---

## ✏️ Step 2: Update Code Constants

In your local repository, update `FIRESTORE_PROJECT_ID` and `GCS_BUCKET_NAME` in `app/agent.py`:

```python
FIRESTORE_PROJECT_ID = "YOUR_NEW_PROJECT_ID"
GCS_BUCKET_NAME = "YOUR_UNIQUE_BUCKET_NAME"
```

---

## 🚀 Step 3: Deploy Agent Backend to Agent Runtime

Run `agents-cli deploy` to build the container image and deploy your agent to Google Cloud Agent Runtime:

```bash
agents-cli deploy --project YOUR_NEW_PROJECT_ID --region us-east1 --no-confirm-project
```

Once deployment completes, note down the returned Reasoning Engine resource name:
`projects/YOUR_NEW_PROJECT_ID/locations/us-east1/reasoningEngines/<REASONING_ENGINE_ID>`

---

## 🌐 Step 4: Run or Deploy the Web Frontend

### Option A: Run Locally
```bash
export AGENT_ENGINE_RESOURCE_NAME="projects/YOUR_NEW_PROJECT_ID/locations/us-east1/reasoningEngines/<REASONING_ENGINE_ID>"
export AGENT_DIRECTORY="app"
cd frontend
uv run python main.py
```
Open `http://localhost:8080` in your browser.

### Option B: Deploy Frontend to Cloud Run (Production)
```bash
cd frontend
gcloud run deploy globetrotter-frontend \
  --source . \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/YOUR_NEW_PROJECT_ID/locations/us-east1/reasoningEngines/<REASONING_ENGINE_ID>"
```
Cloud Run will provide a permanent HTTPS URL for your application.
