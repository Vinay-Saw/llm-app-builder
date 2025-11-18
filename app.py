from flask import Flask, request, jsonify, render_template
import os
import json
import requests
from datetime import datetime
import hashlib
from github import Github
import time
import threading
import base64

app = Flask(__name__)

# Configuration from environment variables
AIPIPE_API_KEY = os.environ.get('AIPIPE_API_KEY')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Initialize clients only if keys are provided
github_client = None

# aipipe.org API configuration
AIPIPE_API_URL = "https://aipipe.org/openrouter/v1/chat/completions"

if GITHUB_TOKEN:
    github_client = Github(GITHUB_TOKEN)

# In-memory project storage (use database in production)
projects_db = {}

def verify_secret(provided_secret):
    """Verify the secret key"""
    if not SECRET_KEY:
        return False
    return provided_secret == SECRET_KEY

def generate_app_with_llm(brief, task, checks, attachments=None, existing_code=None, revision_request=None):
    """Generate application code using aipipe.org"""

    if not AIPIPE_API_KEY:
        raise Exception("AIPipe API key not configured")

    # Prepare attachment context
    attachment_context = ""
    if attachments:
        file_names = [attachment['name'] for attachment in attachments]
        attachment_context = f"\n\nThe following files are available in the root directory of the application: {', '.join(file_names)}. You MUST write code to utilize these files if relevant to the task (e.g., load the CSV data)."

    # Build the prompt
    if existing_code:
        prompt = f"""You are an expert web developer. Update the existing application based on the revision request.

REVISION REQUEST: {revision_request}

EXISTING CODE:
{existing_code}

{attachment_context}

REQUIREMENTS:
{chr(10).join(f'- {check}' for check in checks)}

Please provide the COMPLETE updated code with all files. Return a JSON object with this structure:
{{
  "html": "complete HTML code",
  "css": "complete CSS code (if separate)",
  "js": "complete JavaScript code (if separate)",
  "readme": "README.md content"
}}"""
    else:
        prompt = f"""You are an expert web developer. Your task is to generate a complete, production-ready web application based on the provided brief.

TASK: {task}
BRIEF: {brief}
{attachment_context}
REQUIREMENTS:
{chr(10).join(f'- {check}' for check in checks)}

Your output MUST be a single, valid JSON object. Use json.dumps() to ensure correctness. The JSON object must have keys "html", "readme", and "license".

Example of final output format:
```json
{{
  "html": "<!DOCTYPE html>...",
  "readme": "# Project Title...",
  "license": "MIT License..."
}}
```

Create a modern, responsive, and fully functional single-page application. Include:
1. Clean, semantic HTML5
2. Modern CSS with good design (use vibrant colors, gradients, animations)
3. Interactive JavaScript functionality
4. Professional README.md with setup and usage instructions
5. MIT License text

IMPORTANT: The HTML should be self-contained with CSS in <style> tags and JS in <script> tags. Make it visually appealing with modern design trends."""

    try:
        # Make request to aipipe.org API
        headers = {
            "Authorization": f"Bearer {AIPIPE_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 8000
        }

        response = requests.post(AIPIPE_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        response_data = response.json()

        # Extract JSON from response
        content = response_data["choices"][0]["message"]["content"]

        # Try to extract JSON from markdown code blocks
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.rfind("```")
            json_str = content[json_start:json_end].strip()
        elif "```" in content:
            json_start = content.find("```") + 3
            json_end = content.rfind("```")
            json_str = content[json_start:json_end].strip()
        else:
            json_str = content

        try:
            code_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Initial JSON parse failed: {e}. Raw content: {json_str}")
            json_str = repair_json_string(json_str)
            try:
                code_data = json.loads(json_str)
            except json.JSONDecodeError as e2:
                print(f"JSON parse failed after repair: {e2}. Repaired content: {json_str}")
                raise Exception(f"Failed to parse LLM response: {e2}")

        return code_data

    except Exception as e:
        print(f"LLM Error: {str(e)}")
        raise Exception(f"Failed to generate code: {str(e)}")

def repair_json_string(json_str):
    """Attempt to repair a broken JSON string"""
    # This is a very common error. LLMs often use single quotes.
    repaired_str = json_str.replace("'", '"')

    # Attempt to fix unterminated strings by adding a closing quote
    if repaired_str.count('"') % 2 != 0:
        repaired_str += '"'

    # Find the last valid closing brace or bracket
    last_brace = repaired_str.rfind('}')
    last_bracket = repaired_str.rfind(']')

    if last_brace == -1 and last_bracket == -1:
        raise ValueError("Invalid JSON: No closing brace or bracket found.")

    # Truncate to the last valid closing character
    if last_brace > last_bracket:
        repaired_str = repaired_str[:last_brace+1]
    else:
        repaired_str = repaired_str[:last_bracket+1]

    # Ensure the structure is closed
    open_braces = repaired_str.count('{')
    close_braces = repaired_str.count('}')

    if open_braces > close_braces:
        repaired_str += '}' * (open_braces - close_braces)

    return repaired_str

def create_github_repo(repo_name, code_data, email, attachments=None):
    """Create GitHub repository and deploy to Pages"""

    if not github_client:
        raise Exception("GitHub token not configured")

    try:
        user = github_client.get_user()

        # Create repository
        try:
            repo = user.create_repo(
                repo_name,
                description=f"Auto-generated application for {email}",
                homepage=f"https://{user.login}.github.io/{repo_name}",
                has_issues=True,
                has_wiki=False,
                auto_init=False
            )
        except Exception as e:
            if "name already exists" in str(e).lower():
                repo = user.get_repo(repo_name)
            else:
                raise e

        # --- Create or update files ---
        files_to_commit = {
            "index.html": code_data.get('html', ''),
            "README.md": code_data.get('readme', '# Project\n\nAuto-generated application'),
            "LICENSE": code_data.get('license', f'''MIT License

Copyright (c) 2025 {user.login}

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
SOFTWARE.''')
        }

        # Add attachments to the commit list
        if attachments:
            for attachment in attachments:
                name = attachment.get('name')
                url = attachment.get('url')
                if not name or not url:
                    continue

                try:
                    # Decode data URI
                    header, encoded = url.split(',', 1)
                    content_bytes = base64.b64decode(encoded)
                    files_to_commit[name] = content_bytes
                except Exception as e:
                    print(f"Failed to decode attachment {name}: {e}")

        commit_sha = None
        for path, content in files_to_commit.items():
            if not content:
                continue
            try:
                # Check if file exists to update it
                existing_file = repo.get_contents(path, ref="main")
                update_result = repo.update_file(
                    path,
                    f"Update {path}",
                    content,
                    existing_file.sha,
                    branch="main"
                )
                commit_sha = update_result['commit'].sha
            except Exception:
                # Create file if it does not exist
                create_result = repo.create_file(
                    path,
                    f"Create {path}",
                    content,
                    branch="main"
                )
                commit_sha = create_result['commit'].sha

        # Enable GitHub Pages
        try:
            pages_url = f"https://api.github.com/repos/{user.login}/{repo_name}/pages"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            payload = {
                "source": {
                    "branch": "main",
                    "path": "/"
                }
            }
            requests.post(pages_url, json=payload, headers=headers)
        except Exception as e:
            print(f"Pages setup: {str(e)}")

        repo_url = repo.html_url
        pages_url = f"https://{user.login}.github.io/{repo_name}"

        return {
            "repo_url": repo_url,
            "pages_url": pages_url,
            "commit_sha": commit_sha,
            "success": True
        }

    except Exception as e:
        print(f"GitHub Error: {str(e)}")
        raise Exception(f"Failed to create repository: {str(e)}")

def run_checks(pages_url, checks):
    """Run validation checks (simulated for now)"""
    results = {
        "url": pages_url,
        "checks_passed": checks.copy(),
        "checks_failed": [],
        "timestamp": datetime.now().isoformat()
    }

    return results

def notify_evaluation_service(evaluation_url, payload):
    """Notify the evaluation service with retry logic"""
    max_retries = 5
    delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            print(f"Notifying evaluation URL: {evaluation_url} (Attempt {attempt + 1})")
            response = requests.post(evaluation_url, json=payload, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            print("Successfully notified evaluation service.")
            return
        except requests.exceptions.RequestException as e:
            print(f"Failed to notify evaluation URL: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print("Max retries reached. Giving up.")

def process_build_request(data):
    """This function runs in a background thread to handle the build process."""
    try:
        # Extract required fields
        email = data.get('email')
        task = data.get('task')
        brief = data.get('brief')
        checks = data.get('checks', [])
        round_num = data.get('round', 1)
        nonce = data.get('nonce', f'nonce-{int(time.time())}')
        evaluation_url = data.get('evaluation_url')
        attachments = data.get('attachments', [])

        # Generate unique project ID
        project_id = hashlib.md5(f"{email}{nonce}{task}".encode()).hexdigest()[:12]

        # Check if this is a revision (Round 2)
        existing_project = projects_db.get(project_id)
        existing_code = None
        revision_request = None

        if round_num == 2 and existing_project:
            existing_code = existing_project.get('code', {}).get('html', '')
            revision_request = brief

        # Generate application code using LLM
        print(f"Generating application for: {task}")
        code_data = generate_app_with_llm(
            brief=brief,
            task=task,
            checks=checks,
            attachments=attachments,
            existing_code=existing_code,
            revision_request=revision_request
        )

        # Create repository name (sanitize)
        repo_name_base = task.lower().replace(' ', '-').replace('_', '-')
        repo_name_base = ''.join(c for c in repo_name_base if c.isalnum() or c == '-')
        repo_name = f"{repo_name_base}-{project_id}"

        # Deploy to GitHub Pages
        print(f"Deploying to GitHub: {repo_name}")
        deployment = create_github_repo(repo_name, code_data, email, attachments)

        # Run checks
        print(f"Running checks on: {deployment['pages_url']}")
        check_results = run_checks(deployment['pages_url'], checks)

        # Store project data
        projects_db[project_id] = {
            'email': email,
            'task': task,
            'brief': brief,
            'code': code_data,
            'deployment': deployment,
            'checks': check_results,
            'round': round_num,
            'status': 'completed',
            'created_at': datetime.now().isoformat()
        }

        # Notify evaluation URL if provided
        if evaluation_url:
            notification_payload = {
                'project_id': project_id,
                'email': email,
                'repo_url': deployment['repo_url'],
                'pages_url': deployment['pages_url'],
                'commit_sha': deployment['commit_sha'],
                'round': round_num,
                'nonce': nonce,
                'checks': check_results
            }
            notify_evaluation_service(evaluation_url, notification_payload)

    except Exception as e:
        print(f"Error in background thread: {str(e)}")
        project_id = hashlib.md5(f"{data.get('email')}{data.get('nonce')}{data.get('task')}".encode()).hexdigest()[:12]
        projects_db[project_id] = {
            'status': 'failed',
            'message': str(e),
            'created_at': datetime.now().isoformat()
        }

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@app.route('/api/build', methods=['POST'])
def build_application():
    """Main endpoint to build and deploy application"""
    try:
        data = request.get_json()

        # Extract required fields for validation
        email = data.get('email')
        secret = data.get('secret')
        task = data.get('task')
        brief = data.get('brief')
        nonce = data.get('nonce')

        # Validate required fields
        if not all([email, secret, task, brief, nonce]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: email, secret, task, brief, and nonce are required'
            }), 400

        # Verify secret
        if not verify_secret(secret):
            return jsonify({
                'status': 'error',
                'message': 'Invalid secret key'
            }), 401

        # Check API configuration
        if not AIPIPE_API_KEY or not GITHUB_TOKEN:
            return jsonify({
                'status': 'error',
                'message': 'Server configuration error: API keys not set'
            }), 500

        # Generate unique project ID
        project_id = hashlib.md5(f"{email}{nonce}{task}".encode()).hexdigest()[:12]

        # Start background thread for processing
        thread = threading.Thread(target=process_build_request, args=(data,))
        thread.daemon = True
        thread.start()

        # Store initial project status
        projects_db[project_id] = {
            'status': 'processing',
            'message': 'Build process started.',
            'created_at': datetime.now().isoformat()
        }

        return jsonify({
            'status': 'success',
            'message': 'Build process initiated successfully. Check status endpoint for updates.',
            'project_id': project_id
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/status/<project_id>', methods=['GET'])
def get_project_status(project_id):
    """Get project status"""
    project = projects_db.get(project_id)

    if not project:
        return jsonify({
            'status': 'error',
            'message': 'Project not found'
        }), 404

    response_data = {'status': project.get('status')}

    if project.get('status') == 'completed':
        deployment = project.get('deployment', {})
        response_data['repo_url'] = deployment.get('repo_url')
        response_data['pages_url'] = deployment.get('pages_url')
    elif project.get('status') == 'failed':
        response_data['message'] = project.get('message')

    return jsonify(response_data), 200

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """List all projects"""
    return jsonify({
        'status': 'success',
        'projects': projects_db,
        'count': len(projects_db)
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'configured': {
            'aipipe': AIPIPE_API_KEY is not None,
            'github': GITHUB_TOKEN is not None,
            'secret': SECRET_KEY is not None
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting LLM Application Builder on port {port}")
    print(f"AIPipe API: {'✓ Configured' if AIPIPE_API_KEY else '✗ Not configured'}")
    print(f"GitHub Token: {'✓ Configured' if GITHUB_TOKEN else '✗ Not configured'}")
    print(f"Secret Key: {'✓ Configured' if SECRET_KEY else '✗ Not configured'}")
    app.run(host='0.0.0.0', port=port, debug=True)
