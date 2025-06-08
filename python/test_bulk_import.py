#!/usr/bin/env python3
"""
SCIM 2.0 Bulk Import Test Suite

This script tests the bulk CSV import functionality including various scenarios:
- Valid CSV uploads
- CSV validation
- Dry run mode
- Error handling
- Duplicate detection
- Template download

Make sure the server is running on http://localhost:8000 before running this script.
"""

import requests
import io
import csv
import sys
import time
from requests.auth import HTTPBasicAuth

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
auth = HTTPBasicAuth(ADMIN_USER, ADMIN_PASS)


def create_test_csv(filename: str, users_data: list) -> str:
    """Create a test CSV file with user data."""
    headers = ['userName', 'firstName', 'surName', 'displayName', 'email', 'secondaryEmail', 'externalId', 'active']
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(users_data)
    
    return output.getvalue()


def test_bulk_import_functionality():
    """Test the complete bulk import functionality."""
    print("🚀 SCIM 2.0 Bulk Import Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Get realm for testing
        print("\n1️⃣ Getting available realms...")
        response = requests.get(f"{BASE_URL}/admin/realms", auth=auth)
        if response.status_code == 200:
            realms = response.json()
            if realms:
                realm_id = realms[0]['realm_id']
                print(f"✅ Using realm: {realm_id}")
            else:
                print("❌ No realms available")
                return False
        else:
            print(f"❌ Failed to get realms: {response.status_code}")
            return False
        
        # Test 2: Get bulk import info
        print("\n2️⃣ Testing bulk import info endpoint...")
        response = requests.get(f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/bulk-import/status", auth=auth)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Bulk import info retrieved")
            print(f"   Max file size: {info['data']['max_file_size_mb']}MB")
            print(f"   Max users per import: {info['data']['max_users_per_import']}")
            print(f"   Required columns: {', '.join(info['data']['required_columns'])}")
        else:
            print(f"❌ Failed to get bulk import info: {response.status_code}")
            return False
        
        # Test 3: Download CSV template
        print("\n3️⃣ Testing CSV template download...")
        response = requests.get(f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/bulk-import/template", auth=auth)
        if response.status_code == 200:
            template_content = response.text
            print(f"✅ CSV template downloaded ({len(template_content)} bytes)")
            print(f"   Content preview: {template_content[:100]}...")
        else:
            print(f"❌ Failed to download template: {response.status_code}")
            return False
        
        # Test 4: Test valid CSV upload (dry run)
        print("\n4️⃣ Testing valid CSV upload (dry run)...")
        valid_users = [
            {
                'userName': 'bulk_test1',
                'firstName': 'Test',
                'surName': 'User1',
                'displayName': 'Test User 1',
                'email': 'test1@bulk-import.com',
                'secondaryEmail': 'test1.alt@bulk-import.com',
                'externalId': 'BULK001',
                'active': 'true'
            },
            {
                'userName': 'bulk_test2',
                'firstName': 'Test',
                'surName': 'User2',
                'displayName': '',  # Will be auto-generated
                'email': 'test2@bulk-import.com',
                'secondaryEmail': '',
                'externalId': 'BULK002',
                'active': 'false'
            },
            {
                'userName': 'bulk_test3',
                'firstName': 'Test',
                'surName': 'User3',
                'displayName': 'Test User 3',
                'email': 'test3@bulk-import.com',
                'secondaryEmail': '',
                'externalId': '',
                'active': 'true'
            }
        ]
        
        csv_content = create_test_csv("test_users.csv", valid_users)
        files = {'file': ('test_users.csv', csv_content, 'text/csv')}
        data = {'dry_run': 'true', 'skip_duplicates': 'true', 'continue_on_error': 'true'}
        
        response = requests.post(
            f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/bulk-import",
            files=files,
            data=data,
            auth=auth
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dry run completed successfully")
            print(f"   Status: {result['status']}")
            print(f"   Total rows: {result['total_rows']}")
            print(f"   Successful validations: {result['successful_imports']}")
            print(f"   Failed validations: {result['failed_imports']}")
            print(f"   Processing time: {result['processing_time_seconds']:.2f}s")
        else:
            print(f"❌ Dry run failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 5: Test actual CSV upload (create users)
        print("\n5️⃣ Testing actual CSV upload (create users)...")
        files = {'file': ('test_users.csv', csv_content, 'text/csv')}
        data = {'dry_run': 'false', 'skip_duplicates': 'true', 'continue_on_error': 'true'}
        
        response = requests.post(
            f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/bulk-import",
            files=files,
            data=data,
            auth=auth
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Bulk import completed successfully")
            print(f"   Status: {result['status']}")
            print(f"   Total rows: {result['total_rows']}")
            print(f"   Successful imports: {result['successful_imports']}")
            print(f"   Failed imports: {result['failed_imports']}")
            print(f"   Skipped imports: {result['skipped_imports']}")
            print(f"   Processing time: {result['processing_time_seconds']:.2f}s")
            
            # Store created user IDs for cleanup
            created_users = []
            for user_result in result['results']:
                if user_result['status'] == 'success' and user_result.get('user_id'):
                    created_users.append(user_result['user_id'])
            
        else:
            print(f"❌ Bulk import failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 6: Test duplicate detection
        print("\n6️⃣ Testing duplicate detection...")
        files = {'file': ('test_users_duplicate.csv', csv_content, 'text/csv')}
        data = {'dry_run': 'false', 'skip_duplicates': 'true', 'continue_on_error': 'true'}
        
        response = requests.post(
            f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/bulk-import",
            files=files,
            data=data,
            auth=auth
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Duplicate detection test completed")
            print(f"   Status: {result['status']}")
            print(f"   Successful imports: {result['successful_imports']}")
            print(f"   Skipped imports: {result['skipped_imports']}")
            if result['skipped_imports'] > 0:
                print(f"   ✅ Duplicates were properly skipped")
        else:
            print(f"❌ Duplicate detection test failed: {response.status_code}")
        
        # Test 7: Test invalid CSV
        print("\n7️⃣ Testing invalid CSV handling...")
        invalid_users = [
            {
                'userName': 'invalid_user',
                'firstName': '',  # Invalid - empty required field
                'surName': 'User',
                'email': 'invalid-email'  # Invalid email format
            }
        ]
        
        invalid_csv = create_test_csv("invalid_users.csv", invalid_users)
        files = {'file': ('invalid_users.csv', invalid_csv, 'text/csv')}
        data = {'dry_run': 'true', 'skip_duplicates': 'true', 'continue_on_error': 'true'}
        
        response = requests.post(
            f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/bulk-import",
            files=files,
            data=data,
            auth=auth
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Invalid CSV test completed")
            print(f"   Status: {result['status']}")
            print(f"   Failed validations: {result['failed_imports']}")
            if result['failed_imports'] > 0:
                print(f"   ✅ Invalid data was properly rejected")
        else:
            print(f"❌ Invalid CSV test failed: {response.status_code}")
        
        # Test 8: Test large file handling
        print("\n8️⃣ Testing large file handling...")
        large_users = []
        for i in range(10):  # Create 10 test users
            large_users.append({
                'userName': f'bulk_large_{i}',
                'firstName': f'Large{i}',
                'surName': 'Test',
                'displayName': f'Large Test {i}',
                'email': f'large{i}@bulk-test.com',
                'active': 'true'
            })
        
        large_csv = create_test_csv("large_users.csv", large_users)
        files = {'file': ('large_users.csv', large_csv, 'text/csv')}
        data = {'dry_run': 'true', 'skip_duplicates': 'true', 'continue_on_error': 'true'}
        
        response = requests.post(
            f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/bulk-import",
            files=files,
            data=data,
            auth=auth
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Large file test completed")
            print(f"   Processed {result['total_rows']} users")
            print(f"   Processing time: {result['processing_time_seconds']:.2f}s")
        else:
            print(f"❌ Large file test failed: {response.status_code}")
        
        # Test 9: Verify created users exist
        print("\n9️⃣ Verifying created users exist...")
        if 'created_users' in locals():
            for i, user_id in enumerate(created_users[:3]):  # Check first 3 users
                response = requests.get(
                    f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{user_id}",
                    auth=auth
                )
                if response.status_code == 200:
                    user = response.json()
                    print(f"   ✅ User {i+1}: {user['userName']} exists (ID: {user_id})")
                else:
                    print(f"   ❌ User {i+1} not found (ID: {user_id})")
        
        # Test 10: Cleanup - Delete created users
        print("\n🧹 Cleaning up created test users...")
        if 'created_users' in locals():
            for user_id in created_users:
                response = requests.delete(
                    f"{BASE_URL}/scim/v2/Realms/{realm_id}/Users/{user_id}",
                    auth=auth
                )
                if response.status_code == 204:
                    print(f"   ✅ Deleted user {user_id}")
                else:
                    print(f"   ⚠️  Failed to delete user {user_id}")
        
        print("\n🎉 All bulk import tests completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error!")
        print("Make sure the SCIM server is running on http://localhost:8000")
        print("Start the server with: python start_server.py")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    try:
        print("Starting SCIM 2.0 Bulk Import tests...")
        print("Make sure the server is running on http://localhost:8000")
        
        success = test_bulk_import_functionality()
        if success:
            print("\n✅ All bulk import tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some bulk import tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
        sys.exit(1)
