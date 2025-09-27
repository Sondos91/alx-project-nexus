#!/usr/bin/env python3
"""
Test script to verify authentication and poll creation.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_authentication():
    """Test the authentication flow."""
    print("🔐 Testing Authentication Flow")
    print("=" * 50)
    
    # Test login
    login_data = {
        "username": "superadmin",
        "password": "superadmin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data['key']
        print(f"✅ Login successful! Token: {token[:20]}...")
        
        # Test creating a poll with authentication
        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
        
        poll_data = {
            "title": "Test Poll from Authenticated User",
            "description": "This poll should show the correct creator username",
            "options": [
                {"text": "Option 1"},
                {"text": "Option 2"},
                {"text": "Option 3"}
            ]
        }
        
        print("\n📝 Creating poll with authentication...")
        poll_response = requests.post(f"{BASE_URL}/polls/", json=poll_data, headers=headers)
        print(f"Poll Creation Status: {poll_response.status_code}")
        
        if poll_response.status_code == 201:
            poll_data = poll_response.json()
            print(f"✅ Poll created successfully!")
            print(f"   Poll ID: {poll_data['id']}")
            print(f"   Creator Username: {poll_data.get('creator_username', 'NOT FOUND')}")
            print(f"   Title: {poll_data['title']}")
        else:
            print(f"❌ Poll creation failed: {poll_response.text}")
            
        # Test getting user profile
        print("\n👤 Testing user profile...")
        profile_response = requests.get(f"{BASE_URL}/user/profile/", headers=headers)
        print(f"Profile Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"✅ Profile retrieved!")
            print(f"   Username: {profile_data['username']}")
            print(f"   Email: {profile_data['email']}")
        else:
            print(f"❌ Profile retrieval failed: {profile_response.text}")
            
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_authentication()
