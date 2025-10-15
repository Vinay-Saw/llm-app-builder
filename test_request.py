import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_URL = "http://localhost:5000/api/build"
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def test_round_1():
    """Test Round 1: Initial build"""
    print("=" * 60)
    print("TESTING ROUND 1: Initial Application Build")
    print("=" * 60)
    
    request_data = {
        "email": "student@example.com",
        "secret": SECRET_KEY,
        "task": "Interactive Todo List Application",
        "round": 1,
        "nonce": "ab12-test-001",
        "brief": """Create a modern, responsive todo list web application with the following features:

1. Add new tasks using a text input field and 'Add' button
2. Display tasks in a clean, organized list
3. Mark tasks as complete/incomplete by clicking on them (toggle with visual feedback)
4. Delete individual tasks with a delete button
5. Filter tasks by status: All, Active, Completed
6. Show count of active tasks remaining
7. Use localStorage to persist tasks across browser sessions
8. Implement a 'Clear Completed' button to remove all completed tasks
9. Beautiful, modern UI with smooth animations and transitions
10. Fully responsive design that works on mobile, tablet, and desktop
11. Use a pleasant color scheme (suggestion: blues and whites)
12. Add hover effects and visual feedback for all interactive elements
13. Include a header with the app title
14. Empty state message when no tasks exist

The application should be production-ready with clean, well-structured code.""",
        "checks": [
            "Repo has MIT license",
            "README.md is professionally formatted",
            "README.md contains setup instructions",
            "README.md contains usage instructions",
            "Application is responsive on mobile devices",
            "Tasks persist after page reload",
            "All interactive elements have visual feedback"
        ],
        "evaluation_url": "https://example.com/api/evaluate",
        "attachments": []
    }
    
    try:
        print("\n📤 Sending request...")
        print(f"Task: {request_data['task']}")
        print(f"Round: {request_data['round']}")
        print(f"Using secret: {SECRET_KEY[:10]}...")
        
        response = requests.post(API_URL, json=request_data, timeout=120)
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        result = response.json()
        print(f"\n✅ Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'success':
            print(f"\n🎉 Success!")
            print(f"Project ID: {result.get('project_id')}")
            print(f"Repository: {result.get('repo_url')}")
            print(f"Live Site: {result.get('pages_url')}")
            print(f"\n💡 Tip: GitHub Pages may take 1-2 minutes to build.")
            return result.get('project_id')
        else:
            print(f"\n❌ Error: {result.get('message')}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"\n❌ Request timed out after 120 seconds")
        return None
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error. Is the server running at {API_URL}?")
        return None
    except Exception as e:
        print(f"\n❌ Request failed: {str(e)}")
        return None

def test_round_2(project_id=None):
    """Test Round 2: Revision request"""
    print("\n" + "=" * 60)
    print("TESTING ROUND 2: Application Revision")
    print("=" * 60)
    
    request_data = {
        "email": "student@example.com",
        "secret": SECRET_KEY,
        "task": "Interactive Todo List Application",
        "round": 2,
        "nonce": f"ab12-test-002-{int(time.time())}",
        "brief": """Please make the following improvements to the todo list:

1. Add a dark mode toggle button in the header
2. Add due dates to tasks with a date picker
3. Add a search/filter functionality to find tasks
4. Improve the design with better colors and spacing
5. Add task categories/tags (Work, Personal, Shopping)
6. Add keyboard shortcuts (Enter to add task, Escape to cancel editing)
7. Add task priority levels (High, Medium, Low) with color coding
8. Add sorting options (by date, by priority, alphabetically)

Keep all existing functionality while adding these new features.""",
        "checks": [
            "Repo has MIT license",
            "README.md is professionally formatted",
            "README.md contains setup instructions",
            "README.md contains usage instructions",
            "Application has dark mode toggle",
            "Tasks have due dates",
            "Search functionality works",
            "Keyboard shortcuts are implemented"
        ],
        "evaluation_url": "https://example.com/api/evaluate",
        "attachments": []
    }
    
    try:
        print("\n📤 Sending revision request...")
        print(f"Task: {request_data['task']}")
        print(f"Round: {request_data['round']}")
        if project_id:
            print(f"Project ID: {project_id}")
        
        response = requests.post(API_URL, json=request_data, timeout=120)
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        result = response.json()
        print(f"\n✅ Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'success':
            print(f"\n🎉 Success!")
            print(f"Project ID: {result.get('project_id')}")
            print(f"Repository: {result.get('repo_url')}")
            print(f"Live Site: {result.get('pages_url')}")
            print(f"\n💡 Tip: Changes may take 1-2 minutes to appear on GitHub Pages.")
        else:
            print(f"\n❌ Error: {result.get('message')}")
            
    except requests.exceptions.Timeout:
        print(f"\n❌ Request timed out after 120 seconds")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error. Is the server running at {API_URL}?")
    except Exception as e:
        print(f"\n❌ Request failed: {str(e)}")

def test_with_json_file(filepath):
    """Test with a JSON file matching the request format"""
    print("=" * 60)
    print(f"TESTING WITH JSON FILE: {filepath}")
    print("=" * 60)
    
    try:
        with open(filepath, 'r') as f:
            request_data = json.load(f)
        
        # Add secret if not present or if it's a placeholder
        if 'secret' not in request_data or request_data['secret'] in ['...', '', 'your-secret-key-here']:
            request_data['secret'] = SECRET_KEY
            print(f"\n💡 Using SECRET_KEY from .env file")
        
        print("\n📤 Sending request from file...")
        print(f"Task: {request_data.get('task', 'N/A')}")
        print(f"Round: {request_data.get('round', 1)}")
        
        response = requests.post(API_URL, json=request_data, timeout=120)
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        result = response.json()
        print(f"\n✅ Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'success':
            print(f"\n🎉 Success!")
            print(f"Repository: {result.get('repo_url')}")
            print(f"Live Site: {result.get('pages_url')}")
        else:
            print(f"\n❌ Error: {result.get('message')}")
            
    except FileNotFoundError:
        print(f"\n❌ File not found: {filepath}")
    except json.JSONDecodeError:
        print(f"\n❌ Invalid JSON in file: {filepath}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error. Is the server running at {API_URL}?")
    except Exception as e:
        print(f"\n❌ Request failed: {str(e)}")

def check_status(project_id):
    """Check project status"""
    print("\n" + "=" * 60)
    print(f"CHECKING PROJECT STATUS: {project_id}")
    print("=" * 60)
    
    try:
        response = requests.get(f"http://localhost:5000/api/status/{project_id}")
        result = response.json()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Failed to check status: {str(e)}")

def check_health():
    """Check server health"""
    print("\n" + "=" * 60)
    print("CHECKING SERVER HEALTH")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:5000/health")
        result = response.json()
        print(f"\n✅ Server Status: {result.get('status')}")
        print(f"Timestamp: {result.get('timestamp')}")
        
        config = result.get('configured', {})
        print(f"\nConfiguration:")
        print(f"  Anthropic API: {'✓' if config.get('anthropic') else '✗'}")
        print(f"  GitHub Token: {'✓' if config.get('github') else '✗'}")
        print(f"  Secret Key: {'✓' if config.get('secret') else '✗'}")
        
        if not all(config.values()):
            print(f"\n⚠️  Warning: Some configurations are missing. Check your .env file.")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to server at http://localhost:5000")
        print(f"💡 Make sure the server is running with: python app.py")
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")

if __name__ == "__main__":
    print("\n🚀 LLM Application Builder - Test Suite\n")
    
    # Check if server is running first
    try:
        requests.get("http://localhost:5000/health", timeout=2)
    except:
        print("❌ Server is not running!")
        print("💡 Start the server first with: python app.py")
        print("\nExiting...")
        exit(1)
    
    # Menu
    print("Select test mode:")
    print("1. Test Round 1 (Initial Build)")
    print("2. Test Round 2 (Revision)")
    print("3. Test Both Rounds")
    print("4. Test with JSON file (sample_request.json)")
    print("5. Check project status")
    print("6. Check server health")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        test_round_1()
    elif choice == "2":
        project_id = input("Enter project ID for revision (or press Enter to skip): ").strip()
        test_round_2(project_id if project_id else None)
    elif choice == "3":
        project_id = test_round_1()
        if project_id:
            print("\n⏳ Waiting 5 seconds before testing Round 2...")
            time.sleep(5)
            test_round_2(project_id)
    elif choice == "4":
        filepath = input("Enter JSON file path (default: sample_request.json): ").strip()
        if not filepath:
            filepath = "sample_request.json"
        test_with_json_file(filepath)
    elif choice == "5":
        project_id = input("Enter project ID: ").strip()
        if project_id:
            check_status(project_id)
        else:
            print("❌ Project ID is required")
    elif choice == "6":
        check_health()
    else:
        print("Invalid choice!")
