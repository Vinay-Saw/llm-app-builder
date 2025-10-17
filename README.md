# LLM Application Builder

This project is a fully automated web application builder that receives API requests, uses an AI model (via aipipe.org) to generate complete web applications, and deploys them to GitHub Pages. It supports multi-round revisions, file attachments, and asynchronous processing.

## 📋 Table of Contents

1.  [Project Summary](#-project-summary)
2.  [Features](#-features)
3.  [File Structure](#-file-structure)
4.  [Setup and Installation](#-setup-and-installation)
5.  [Usage Guide](#-usage-guide)
6.  [API Endpoints](#-api-endpoints)
7.  [Code Explanation](#-code-explanation)
8.  [License](#-license)

---

## 🎯 Project Summary

This application serves as a powerful backend service that automates the entire lifecycle of creating and deploying simple web applications. A user sends a JSON request describing an application, and the service handles the rest:

1.  **Receives Request:** A Flask API endpoint accepts a JSON payload with the application brief.
2.  **Generates Code:** It calls the `aipipe.org` API to generate HTML, CSS, JavaScript, and documentation based on the brief.
3.  **Handles Attachments:** Decodes and includes file attachments (like images) from the request.
4.  **Deploys to GitHub:** Creates a new public GitHub repository, commits the generated files, and enables GitHub Pages.
5.  **Asynchronous Workflow:** Immediately acknowledges the request and performs the build in the background to prevent timeouts.
6.  **Notifies on Completion:** Sends a POST request to a specified `evaluation_url` with the deployment details.
7.  **Supports Revisions:** Handles multi-round requests to revise and update the same application.

---

## ✨ Features

-   **AI-Powered Code Generation:** Uses `aipipe.org` (with GPT-4) to generate application code.
-   **Automated GitHub Deployment:** Creates repositories and deploys to GitHub Pages automatically.
-   **Asynchronous Processing:** Handles long-running build jobs in a background thread for a non-blocking API.
-   **File Attachment Support:** Can decode Base64 data URIs and include files in the generated project.
-   **Multi-Round Revisions:** Supports iterative development by accepting "Round 2" requests to modify existing applications.
-   **Resilient Notifications:** Includes a retry mechanism with exponential backoff when notifying evaluation services.
-   **Secure Configuration:** Manages all secret keys (API keys, tokens) using a `.env` file.

---

## 📁 File Structure

```
.
├── app.py                # Main Flask application with all core logic
├── requirements.txt      # Python dependencies for the project
├── procfile.txt          # Configuration for deploying to cloud services like Heroku
├── test_request.py       # Script for testing the /api/build endpoint
├── test_aipipe.py        # Diagnostic script to test the aipipe.org API connection
├── sample_request.json   # Example JSON request for an initial build
└── templates/
    └── index.html        # Simple frontend for the service (optional)
```

---

## 🛠️ Setup and Installation

### Prerequisites

-   Python 3.8+
-   Git

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

```bash
# Create the virtual environment
python -m venv .venv

# Activate the environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a file named `.env` in the root of the project and add your secret keys.

```bash
# .env file

# Get your token from https://aipipe.org/
AIPIPE_API_KEY="your-aipipe-token-here"

# Create a GitHub token with repo, workflow, and admin:repo_hook scopes
GITHUB_TOKEN="your-github-personal-access-token-here"

# Create a strong, unique secret for validating requests
SECRET_KEY="your-custom-secret-key-here"
```

---

## 🚀 Usage Guide

### 1. Start the Application

Run the Flask server from your terminal.

```bash
python app.py
```

The server will start on `http://localhost:5000`.

### 2. Send a Build Request

Use a tool like `curl` to send a JSON request to the build endpoint.

#### Round 1: Initial Build

This command will create a new application.

```bash
curl -X POST https://llm-app-builder-production.up.railway.app/api/build -H "Content-Type: application/json" -d @sample_request.json
```
```powershell
Invoke-RestMethod -Uri "https://llm-app-builder-production.up.railway.app/api/build" -Method POST -ContentType "application/json" -Body (Get-Content -Raw -Path "sample_request.json")
```

You will receive an immediate response with a `project_id`.

#### Round 2: Revise the Application

After the first round is complete, send the second request to modify the application. *Specify "Round":2*

```bash
curl -X POST https://llm-app-builder-production.up.railway.app/api/build -H "Content-Type: application/json" -d @sample_request.json
```
```powershell
Invoke-RestMethod -Uri "https://llm-app-builder-production.up.railway.app/api/build" -Method POST -ContentType "application/json" -Body (Get-Content -Raw -Path "sample_request.json")
```

### 3. Check the Status

You can check the progress of a build using the `/api/status/<project_id>` endpoint.

```bash
curl http://localhost:5000/api/status/your-project-id-here
```

---

## 🔌 API Endpoints

-   **`POST /api/build`**: The main endpoint to request a new build or a revision. It accepts a JSON body and initiates the build process in the background.
-   **`GET /api/status/<project_id>`**: Returns the current status of a build (`processing`, `completed`, or `failed`) and the final deployment details.
-   **`GET /api/projects`**: Lists all projects that have been processed by the service.
-   **`GET /health`**: A health check endpoint that confirms the server is running and API keys are configured.

---

## 💻 Code Explanation

-   **`build_application()`**: The main API endpoint that validates the request, starts the background processing thread, and returns an immediate `202 Accepted` response.
-   **`process_build_request()`**: The core function that runs in the background. It orchestrates the entire workflow: calling the LLM, creating the repository, and notifying the evaluation service.
-   **`generate_app_with_llm()`**: Constructs the prompt and calls the `aipipe.org` API to generate the application code.
-   **`create_github_repo()`**: Handles all interactions with the GitHub API, including creating/updating files, handling attachments, and enabling GitHub Pages.
-   **`notify_evaluation_service()`**: Sends the final notification to the `evaluation_url` with a robust retry mechanism.
-   **`repair_json_string()`**: A utility function to fix common formatting errors in the AI model's JSON response.

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for full details.

```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```


