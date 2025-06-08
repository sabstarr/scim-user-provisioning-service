#!/usr/bin/env python3
"""
SCIM 2.0 Endpoints Test Suite

This script demonstrates the complete SCIM API functionality including email updates.
Make sure the server is running on http://localhost:8000 before running this script.
"""

import requests
import json
import sys
from requests.auth import HTTPBasicAuth

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
auth = HTTPBasicAuth(ADMIN_USER, ADMIN_PASS)

def test_api():
    """Test the complete SCIM API functionality."""
    print("🚀 SCIM 2.0 Endpoints Test Suite")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    response = requests.get(f"{BASE_URL}/admin/health", auth=auth)
    if response.status_code == 200:
        print("✅ Health check passed")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False
    
    # Test 2: List Realms
    print("\n2️⃣ Testing Realm Listing...")
    response = requests.get(f"{BASE_URL}/admin/realms", auth=auth)
    if response.status_code == 200:
        realms = response.json()
        print(f"✅ Found {len(realms)} realms")
        realm_id = realms[0]["realm_id"]  # Use first realm for testing
        print(f"   Using realm: {realm_id}")
    else:
        print(f"❌ Realm listing failed: {response.status_code}")
        return False
    
    # Test 3: Create SCIM User
    print("\n3️⃣ Testing SCIM User Creation...")
    user_data = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": "jdoe123",
        "firstName": "John",
        "surName": "Doe", 
        "displayName": "John Doe",
        "emails": [{"value": "john.doe@example.com", "primary": True}],
        "active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users",
        json=user_data,
        headers={"Content-Type": "application/scim+json", "Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 201:
        user = response.json()
        user_id = user["id"]
        print(f"✅ User created successfully")
        print(f"   User ID: {user_id}")
        print(f"   Username: {user['userName']}")
    else:
        print(f"❌ User creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Test 4: Get User by ID
    print("\n4️⃣ Testing SCIM User Retrieval...")
    response = requests.get(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{user_id}",
        headers={"Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 200:
        retrieved_user = response.json()
        print(f"✅ User retrieved successfully")
        print(f"   Display Name: {retrieved_user['displayName']}")
    else:
        print(f"❌ User retrieval failed: {response.status_code}")
    
    # Test 5: Update User
    print("\n5️⃣ Testing SCIM User Update...")
    update_data = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": "jdoe123",
        "firstName": "John",
        "surName": "Doe",
        "displayName": "John Updated Doe",
        "emails": [{"value": "john.doe@example.com", "primary": True}],
        "active": True
    }
    
    response = requests.put(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{user_id}",
        json=update_data,
        headers={"Content-Type": "application/scim+json", "Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 200:
        updated_user = response.json()
        print(f"✅ User updated successfully")
        print(f"   Updated Display Name: {updated_user['displayName']}")
    else:
        print(f"❌ User update failed: {response.status_code}")
    
    # Test 6: List Users
    print("\n6️⃣ Testing SCIM User Listing...")
    response = requests.get(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users",
        headers={"Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 200:
        users_response = response.json()
        print(f"✅ Found {users_response['totalResults']} users in realm")
    else:
        print(f"❌ User listing failed: {response.status_code}")
    
    # Test 7: Find User by Username
    print("\n7️⃣ Testing Username Lookup...")
    response = requests.get(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/by-username/jdoe123",
        headers={"Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 200:
        found_user = response.json()
        print(f"✅ User found by username: {found_user['displayName']}")
    else:
        print(f"❌ Username lookup failed: {response.status_code}")
    
    # Test 8: Delete User
    print("\n8️⃣ Testing SCIM User Deletion...")
    response = requests.delete(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{user_id}",
        headers={"Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 204:
        print("✅ User deleted successfully")
    else:
        print(f"❌ User deletion failed: {response.status_code}")
    
    # Test 9: Verify Deletion
    print("\n9️⃣ Verifying User Deletion...")
    response = requests.get(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{user_id}",
        headers={"Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 404:
        print("✅ User deletion verified - user not found")
    else:
        print(f"❌ User deletion verification failed: {response.status_code}")
    
    # Test 10: Email Update Testing - Create user for email tests
    print("\n🔟 Testing Email Updates - Creating test user...")
    email_user_data = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": "emailtest123",
        "firstName": "Email",
        "surName": "Test",
        "displayName": "Email Test User",
        "emails": [{"value": "original@example.com", "primary": True}],
        "active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users",
        json=email_user_data,
        headers={"Content-Type": "application/scim+json", "Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code != 201:
        print(f"❌ Email test user creation failed: {response.status_code}")
        return False
    
    email_user = response.json()
    email_user_id = email_user["id"]
    print(f"✅ Email test user created: {email_user_id}")
    print(f"   Original email: {email_user['emails'][0]['value']}")
    
    # Test 10a: Single email update
    print("\n🔟a Testing single email update via PUT...")
    single_email_update = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": "emailtest123",
        "firstName": "Email",
        "surName": "Test",
        "displayName": "Email Test User",
        "emails": [{"value": "updated@example.com", "primary": True}],
        "active": True
    }
    
    response = requests.put(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{email_user_id}",
        json=single_email_update,
        headers={"Content-Type": "application/scim+json", "Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 200:
        updated_user = response.json()
        print(f"✅ Single email update successful")
        print(f"   New email: {updated_user['emails'][0]['value']}")
    else:
        print(f"❌ Single email update failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test 11: Multiple email update
    print("\n1️⃣1️⃣ Testing multiple email update via PUT...")
    multiple_email_update = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": "emailtest123",
        "firstName": "Email",
        "surName": "Test",
        "displayName": "Email Test User",
        "emails": [
            {"value": "primary@example.com", "primary": True},
            {"value": "secondary@example.com", "primary": False}
        ],
        "active": True
    }
    
    response = requests.put(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{email_user_id}",
        json=multiple_email_update,
        headers={"Content-Type": "application/scim+json", "Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 200:
        updated_user = response.json()
        print(f"✅ Multiple email update successful")
        print(f"   Emails: {len(updated_user['emails'])} total")
        for i, email in enumerate(updated_user['emails']):
            print(f"     {i+1}. {email['value']} (primary: {email['primary']})")
    else:
        print(f"❌ Multiple email update failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test 11a: Verify email persistence
    print("\n1️⃣1️⃣a Verifying email updates persistence...")
    response = requests.get(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{email_user_id}",
        headers={"Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 200:
        final_user = response.json()
        print(f"✅ Email persistence verified")
        print(f"   Final emails: {[email['value'] for email in final_user['emails']]}")
    else:
        print(f"❌ Email persistence verification failed: {response.status_code}")
    
    # Clean up email test user
    print("\n🧹 Cleaning up email test user...")
    response = requests.delete(
        f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{email_user_id}",
        headers={"Accept": "application/scim+json"},
        auth=auth
    )
    
    if response.status_code == 204:
        print("✅ Email test user deleted successfully")
    else:
        print(f"⚠️ Email test user deletion failed: {response.status_code}")
    
    print("\n🎉 SCIM API Test Suite Completed!")
    return True


if __name__ == "__main__":
    try:
        print("Starting SCIM 2.0 API tests...")
        print("Make sure the server is running on http://localhost:8000")
        
        success = test_api()
        if success:
            print("\n✅ All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the SCIM server is running on http://localhost:8000")
        print("Start the server with: python start_server.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test suite failed with error: {str(e)}")
        sys.exit(1)
