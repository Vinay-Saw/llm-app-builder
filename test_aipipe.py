"""
Test script to verify AIPipe.org integration
Run this to test if your AIPipe API key is working correctly.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_aipipe_api():
    """Test the AIPipe.org API integration"""
    
    # Get API key from environment
    api_key = os.environ.get('AIPIPE_API_KEY')
    
    if not api_key:
        print("❌ AIPIPE_API_KEY not found in environment variables")
        print("   Make sure your .env file contains: AIPIPE_API_KEY=your-token-here")
        return False
    
    print("✓ Found AIPipe API key")
    print(f"   Key: {api_key[:20]}...")
    
    # Test API endpoint
    api_url = "https://aipipe.org/openrouter/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": "Say 'Hello from AIPipe!' and nothing else."}],
        "max_tokens": 50
    }
    
    try:
        print("\n🔄 Testing AIPipe.org API...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            print(f"   Response: {content}")
            print("✅ AIPipe.org API is working correctly!")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {str(e)}")
        print("   Check your internet connection and try again")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {str(e)}")
        print("   Invalid response format")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False

def test_environment_config():
    """Test all environment variables"""
    
    print("🔧 Checking Environment Configuration...")
    
    # Required variables
    required_vars = {
        'AIPIPE_API_KEY': 'AIPipe.org API key',
        'GITHUB_TOKEN': 'GitHub Personal Access Token', 
        'SECRET_KEY': 'Flask secret key'
    }
    
    all_configured = True
    
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"   ✓ {var}: Configured ({description})")
        else:
            print(f"   ❌ {var}: Not configured ({description})")
            all_configured = False
    
    return all_configured

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AIPipe.org Integration Test")
    print("=" * 60)
    
    # Test environment configuration
    env_ok = test_environment_config()
    
    if not env_ok:
        print("\n❌ Environment configuration incomplete")
        print("   Update your .env file with all required variables")
        exit(1)
    
    # Test AIPipe API
    api_ok = test_aipipe_api()
    
    print("\n" + "=" * 60)
    if api_ok:
        print("🎉 All tests passed! Your AIPipe.org integration is ready.")
        print("   You can now run: python app.py")
    else:
        print("❌ Tests failed. Please check your configuration.")
        print("   Refer to MIGRATION.md for troubleshooting steps.")
    print("=" * 60)