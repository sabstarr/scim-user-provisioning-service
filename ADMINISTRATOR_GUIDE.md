# SCIM 2.0 User Provisioning Service - Administrator Guide

## 📋 Table of Contents

1. [Service Overview](#service-overview)
2. [Starting and Stopping the Service](#starting-and-stopping-the-service)
3. [Understanding Realms](#understanding-realms)
4. [Authentication](#authentication)
5. [Administrative Endpoints](#administrative-endpoints)
6. [SCIM User Management Endpoints](#scim-user-management-endpoints)
7. [API Examples](#api-examples)
8. [Troubleshooting](#troubleshooting)
9. [Security Best Practices](#security-best-practices)

---

## Service Overview

The SCIM 2.0 User Provisioning Service is a comprehensive API for enterprise user management that supports:

- **Multi-tenant architecture** with realm-based user isolation
- **SCIM 2.0 compliance** for industry-standard user provisioning
- **RESTful API** with comprehensive documentation
- **Secure authentication** using HTTP Basic Auth
- **Real-time user management** with full CRUD operations

### Key Components
- **FastAPI Application**: Modern Python web framework
- **SQLite Database**: Lightweight, file-based storage
- **Multi-Realm Support**: Tenant isolation for enterprise environments
- **HTTP Basic Authentication**: Simple, secure API access

---

## Starting and Stopping the Service

### Prerequisites
- Python 3.8 or higher
- Required dependencies installed (`pip install -r requirements.txt`)

### Starting the Service

**Method 1: Simple Startup (Recommended)**
```powershell
cd c:\codes\python_projects\scim-endpoints-project\python
python start_server.py
```

**Method 2: Advanced Startup**
```powershell
cd c:\codes\python_projects\scim-endpoints-project\python
python -m src.run_server
```

### Service Startup Process
When started, the service will:
1. **Initialize Database** - Create tables and default data
2. **Create Default Realms** - Set up initial tenant spaces
3. **Create Admin User** - Default authentication credentials
4. **Start HTTP Server** - Listen on http://localhost:8000

### Expected Startup Output
```
INFO: Starting SCIM 2.0 Endpoints Server...
INFO: Initializing database...
INFO: Database tables created successfully
INFO: Server will be available at:
INFO:   - HTTP: http://localhost:8000
INFO:   - API Documentation: http://localhost:8000/docs
INFO: Default admin credentials: admin/admin123
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Stopping the Service
- **Windows**: Press `Ctrl+C` in the terminal
- **PowerShell**: Use `Stop-Process` if running as background service

### Service Health Check
```bash
curl -u admin:admin123 http://localhost:8000/admin/health
```

Expected Response:
```json
{
    "message": "SCIM endpoints are healthy",
    "data": {
        "admin": "admin",
        "status": "active"
    }
}
```

---

## Understanding Realms

### What is a Realm?
A **realm** is a logical tenant space that provides complete user isolation in multi-tenant environments. Each realm:
- Contains its own set of users
- Has a unique identifier (e.g., `realm_c308a7df`)
- Provides complete data isolation between tenants
- Supports independent user provisioning

### Default Realms
The service creates two default realms:
1. **SCIM Users Realm** (`realm_c308a7df`) - Primary user provisioning
2. **SCIM IDP Realm** (`realm_a3d6898b`) - Identity Provider integration

### Realm Structure
```json
{
    "id": 1,
    "realm_id": "realm_c308a7df",
    "name": "SCIM Users Realm",
    "description": "Default realm for SCIM user provisioning",
    "created_at": "2025-06-08T14:10:09"
}
```

### Selecting the Appropriate Realm

**For Production Environments:**
- Use dedicated realms per customer/tenant
- Create descriptive realm names for easy identification
- Document realm purposes and ownership

**For Development/Testing:**
- Use separate realms for different testing scenarios
- Create temporary realms for integration testing
- Clean up test realms regularly

---

## Authentication

### HTTP Basic Authentication
All API endpoints require HTTP Basic Authentication:
- **Default Username**: `admin`
- **Default Password**: `admin123`

### Authentication Headers
```bash
# Method 1: Using curl -u flag
curl -u admin:admin123 http://localhost:8000/endpoint

# Method 2: Using Authorization header
curl -H "Authorization: Basic YWRtaW46YWRtaW4xMjM=" http://localhost:8000/endpoint
```

### Security Considerations
⚠️ **Important**: Change default credentials in production environments!

---

## Administrative Endpoints

### 1. Health Check
**Endpoint**: `GET /admin/health`
**Purpose**: Verify service availability and admin authentication

```bash
curl -u admin:admin123 http://localhost:8000/admin/health
```

**Response**:
```json
{
    "message": "SCIM endpoints are healthy",
    "data": {
        "admin": "admin",
        "status": "active"
    }
}
```

### 2. List All Realms
**Endpoint**: `GET /admin/realms`
**Purpose**: Retrieve all available realms

```bash
curl -u admin:admin123 http://localhost:8000/admin/realms
```

**Response**:
```json
[
    {
        "id": 1,
        "realm_id": "realm_c308a7df",
        "name": "SCIM Users Realm",
        "description": "Default realm for SCIM user provisioning",
        "created_at": "2025-06-08T14:10:09"
    }
]
```

### 3. Get Specific Realm
**Endpoint**: `GET /admin/realms/{realm_id}`
**Purpose**: Retrieve details for a specific realm

```bash
curl -u admin:admin123 http://localhost:8000/admin/realms/realm_c308a7df
```

### 4. Create New Realm
**Endpoint**: `POST /admin/realms`
**Purpose**: Create a new tenant realm

```bash
curl -u admin:admin123 -X POST http://localhost:8000/admin/realms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer ABC Realm",
    "description": "Dedicated realm for Customer ABC users"
  }'
```

**Response**:
```json
{
    "id": 3,
    "realm_id": "realm_abc123def",
    "name": "Customer ABC Realm",
    "description": "Dedicated realm for Customer ABC users",
    "created_at": "2025-06-08T15:30:45"
}
```

### 5. Create Admin User
**Endpoint**: `POST /admin/users`
**Purpose**: Create additional admin users

```bash
curl -u admin:admin123 -X POST http://localhost:8000/admin/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin2",
    "password": "secure_password_123",
    "email": "admin2@company.com"
  }'
```

---

## SCIM User Management Endpoints

### 1. Create SCIM User
**Endpoint**: `POST /scim/v2/Realms/{realm_id}/Users`
**Purpose**: Provision a new user in the specified realm

```bash
curl -u admin:admin123 -X POST \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users \
  -H "Content-Type: application/json" \
  -d '{
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    "userName": "jdoe",
    "firstName": "John",
    "surName": "Doe",
    "displayName": "John Doe",
    "active": true,
    "emails": [
      {
        "value": "john.doe@company.com",
        "primary": true
      }
    ]
  }'
```

**Response**:
```json
{
    "id": "c40157f5-7405-421b-8a72-6171de4a524b",
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    "userName": "jdoe",
    "firstName": "John",
    "surName": "Doe",
    "displayName": "John Doe",
    "active": true,
    "emails": [
        {
            "value": "john.doe@company.com",
            "primary": true
        }
    ],
    "meta": {
        "resourceType": "User",
        "created": "2025-06-08T15:08:17",
        "lastModified": "2025-06-08T15:08:17",
        "location": "/scim/v2/Realms/realm_c308a7df/Users/c40157f5-7405-421b-8a72-6171de4a524b"
    }
}
```

### 2. Retrieve User by ID
**Endpoint**: `GET /scim/v2/Realms/{realm_id}/Users/{user_id}`
**Purpose**: Get a specific user using their unique ID

```bash
curl -u admin:admin123 \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users/c40157f5-7405-421b-8a72-6171de4a524b
```

### 3. Update User
**Endpoint**: `PUT /scim/v2/Realms/{realm_id}/Users/{user_id}`
**Purpose**: Update user attributes

```bash
curl -u admin:admin123 -X PUT \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users/c40157f5-7405-421b-8a72-6171de4a524b \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "jdoe",
    "firstName": "John",
    "surName": "Doe",
    "displayName": "John Updated Doe",
    "active": true,
    "emails": [
      {
        "value": "john.updated@company.com",
        "primary": true
      },
      {
        "value": "john.secondary@company.com",
        "primary": false
      }
    ]
  }'
```

### 4. List Users
**Endpoint**: `GET /scim/v2/Realms/{realm_id}/Users`
**Purpose**: Retrieve all users in a realm with pagination

```bash
curl -u admin:admin123 \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users
```

**Response**:
```json
{
    "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
    "totalResults": 1,
    "startIndex": 1,
    "itemsPerPage": 1,
    "Resources": [
        {
            "id": "c40157f5-7405-421b-8a72-6171de4a524b",
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "userName": "jdoe",
            "firstName": "John",
            "surName": "Doe",
            "displayName": "John Doe",
            "active": true,
            "emails": [
                {
                    "value": "john.doe@company.com",
                    "primary": true
                }
            ],
            "meta": {
                "resourceType": "User",
                "created": "2025-06-08T15:08:17",
                "lastModified": "2025-06-08T15:08:17",
                "location": "/scim/v2/Realms/realm_c308a7df/Users/c40157f5-7405-421b-8a72-6171de4a524b"
            }
        }
    ]
}
```

### 5. Find User by Username
**Endpoint**: `GET /scim/v2/Realms/{realm_id}/Users/by-username/{username}`
**Purpose**: Locate user using their username

```bash
curl -u admin:admin123 \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users/by-username/jdoe
```

### 6. Find User by Email
**Endpoint**: `GET /scim/v2/Realms/{realm_id}/Users/by-email/{email}`
**Purpose**: Locate user using their email address

```bash
curl -u admin:admin123 \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users/by-email/john.doe@company.com
```

### 7. Delete User
**Endpoint**: `DELETE /scim/v2/Realms/{realm_id}/Users/{user_id}`
**Purpose**: Remove user from the realm

```bash
curl -u admin:admin123 -X DELETE \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users/c40157f5-7405-421b-8a72-6171de4a524b
```

**Response**: HTTP 204 No Content (successful deletion)

---

## API Examples

### Complete User Lifecycle Example

#### 1. Start Service and Check Health
```bash
# Start the service
python start_server.py

# Check health
curl -u admin:admin123 http://localhost:8000/admin/health
```

#### 2. List Available Realms
```bash
curl -u admin:admin123 http://localhost:8000/admin/realms
```

#### 3. Create a User
```bash
curl -u admin:admin123 -X POST \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "alice.smith",
    "firstName": "Alice",
    "surName": "Smith",
    "displayName": "Alice Smith",
    "active": true,
    "emails": [{"value": "alice.smith@company.com", "primary": true}]
  }'
```

#### 4. Retrieve the User
```bash
# Using the returned user ID
curl -u admin:admin123 \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users/{user_id}
```

#### 5. Update the User
```bash
curl -u admin:admin123 -X PUT \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users/{user_id} \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "alice.smith",
    "firstName": "Alice",
    "surName": "Johnson",
    "displayName": "Alice Johnson",
    "active": true,
    "emails": [{"value": "alice.johnson@company.com", "primary": true}]
  }'
```

#### 6. List All Users
```bash
curl -u admin:admin123 \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users
```

#### 7. Find User by Username
```bash
curl -u admin:admin123 \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users/by-username/alice.smith
```

#### 8. Delete the User
```bash
curl -u admin:admin123 -X DELETE \
  http://localhost:8000/scim/v2/Realms/realm_c308a7df/Users/{user_id}
```

### Bulk Operations Example

#### Create Multiple Users in Different Realms
```bash
# Create realm for Customer A
curl -u admin:admin123 -X POST http://localhost:8000/admin/realms \
  -H "Content-Type: application/json" \
  -d '{"name": "Customer A", "description": "Customer A Users"}'

# Create realm for Customer B  
curl -u admin:admin123 -X POST http://localhost:8000/admin/realms \
  -H "Content-Type: application/json" \
  -d '{"name": "Customer B", "description": "Customer B Users"}'

# Create user in Customer A realm
curl -u admin:admin123 -X POST \
  http://localhost:8000/scim/v2/Realms/{realm_a_id}/Users \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "customer_a_user1",
    "firstName": "User",
    "surName": "One",
    "displayName": "Customer A User 1",
    "active": true,
    "emails": [{"value": "user1@customera.com", "primary": true}]
  }'

# Create user in Customer B realm
curl -u admin:admin123 -X POST \
  http://localhost:8000/scim/v2/Realms/{realm_b_id}/Users \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "customer_b_user1",
    "firstName": "User",
    "surName": "One",
    "displayName": "Customer B User 1",
    "active": true,
    "emails": [{"value": "user1@customerb.com", "primary": true}]
  }'
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Service Won't Start
**Problem**: Server fails to start or exits immediately
**Solutions**:
- Check Python version: `python --version` (requires 3.8+)
- Verify dependencies: `pip install -r requirements.txt`
- Check port availability: Ensure port 8000 is not in use
- Review logs for specific error messages

#### 2. Authentication Failures
**Problem**: API returns 401 Unauthorized
**Solutions**:
- Verify credentials: Default is `admin:admin123`
- Check Basic Auth format: `curl -u username:password`
- Ensure admin user exists in database

#### 3. User Not Found Errors
**Problem**: API returns 404 for existing users
**Solutions**:
- Verify realm ID is correct
- Check user ID format (should be UUID)
- Ensure user exists in the specified realm
- Users are realm-isolated - check the correct realm

#### 4. Database Issues
**Problem**: Database errors or corruption
**Solutions**:
- Delete `scim_database.db` file to reset
- Restart service to recreate default data
- Check file permissions for database file

#### 5. JSON Parsing Errors
**Problem**: API returns JSON decode errors
**Solutions**:
- Validate JSON format using online validators
- Check Content-Type header: `application/json`
- Escape quotes properly in shell commands
- Use proper PowerShell JSON formatting

### Diagnostic Commands

#### Check Service Status
```bash
curl -u admin:admin123 http://localhost:8000/health
```

#### List All Realms
```bash
curl -u admin:admin123 http://localhost:8000/admin/realms
```

#### Count Users in Realm
```bash
curl -u admin:admin123 http://localhost:8000/scim/v2/Realms/{realm_id}/Users
```

#### Test Authentication
```bash
curl -u admin:admin123 http://localhost:8000/admin/health
```

---

## Security Best Practices

### 1. Authentication Security
- **Change Default Credentials**: Never use `admin:admin123` in production
- **Strong Passwords**: Use complex passwords for admin accounts
- **Regular Rotation**: Change passwords periodically
- **Limited Access**: Only provide access to authorized personnel

### 2. Network Security
- **Firewall Rules**: Restrict access to port 8000
- **VPN Access**: Require VPN for remote access
- **Load Balancer**: Use reverse proxy for production deployments
- **SSL/TLS**: Consider adding HTTPS for production (currently HTTP-only)

### 3. Data Protection
- **Database Backups**: Regular backups of `scim_database.db`
- **Access Logging**: Monitor API access patterns
- **Data Retention**: Implement user data retention policies
- **Compliance**: Follow GDPR/CCPA requirements for user data

### 4. Operational Security
- **Log Monitoring**: Review application logs regularly
- **Update Management**: Keep Python and dependencies updated
- **Resource Limits**: Monitor CPU and memory usage
- **Backup Strategy**: Implement regular database backups

### 5. API Security
- **Rate Limiting**: Implement API rate limiting for production
- **Input Validation**: All inputs are validated by Pydantic schemas
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **Error Handling**: Proper error responses without sensitive information

---

## Support and Documentation

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Additional Resources
- **SCIM 2.0 Specification**: RFC 7643 and RFC 7644
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/

### Getting Help
For technical issues:
1. Check the troubleshooting section above
2. Review application logs for error details
3. Verify API documentation at `/docs` endpoint
4. Test with provided examples
5. Check system requirements and dependencies

---

*This guide provides comprehensive instructions for administering the SCIM 2.0 User Provisioning Service. For technical implementation details, refer to the project's README.md and IMPLEMENTATION_SUMMARY.md files.*
