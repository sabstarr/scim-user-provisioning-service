# SCIM 2.0 Endpoints Project

A comprehensive SCIM 2.0 compliant API implementation using FastAPI, SQLAlchemy, and SQLite3 for user provisioning with multi-realm support, secure authentication, and a beautiful modern web frontend.

## 🚀 Features

- **SCIM 2.0 Compliance**: Full implementation of SCIM 2.0 core schema for users
- **Multi-Realm Support**: Isolated user provisioning across different realms/tenants
- **Modern Web Frontend**: Professional single-page application with comprehensive CRUD operations
- **Theme Support**: Light/dark themes with professional toggle switch and system preference detection
- **Complete User Management**: Full Create, Read, Update, Delete operations with advanced search
- **Bulk CSV Import**: Enterprise-grade bulk user provisioning with validation and error reporting
- **Schema Documentation**: Complete SCIM 2.0 user schema reference built into the interface
- **Secure Authentication**: HTTP Basic Authentication with comprehensive session management
- **RESTful API**: FastAPI-based endpoints with automatic OpenAPI documentation
- **Database Security**: SQLAlchemy ORM preventing SQL injection attacks
- **Comprehensive Logging**: Structured logging throughout the application
- **Type Safety**: Full type hints following PEP 8 conventions
- **Mobile Responsive**: Touch-optimized interface that works on all devices

## 📁 Project Structure

```
scim-endpoints-project/
├── frontend/
│   ├── index.html                   # Modern web frontend application
│   ├── styles.css                   # Beautiful styling with light/dark themes
│   └── script.js                    # Secure JavaScript with SCIM integration
├── python/
│   ├── requirements.txt              # Python dependencies
│   ├── start_server.py               # Simple server startup script (stable)
│   ├── src/
│   │   ├── app.py                   # Main FastAPI application
│   │   ├── models.py                # SQLAlchemy database models
│   │   ├── schemas.py               # Pydantic validation schemas
│   │   ├── database_service.py      # Database operations service
│   │   ├── auth_service.py          # Authentication service
│   │   ├── bulk_import_service.py   # CSV bulk import service
│   │   ├── init_db.py              # Database initialization script
│   │   ├── run_server.py           # Development server startup script (auto-reload)
│   │   └── endpoints/
│   │       ├── __init__.py         # Endpoints module initialization
│   │       ├── scim_endpoints.py   # SCIM 2.0 user endpoints
│   │       └── admin_endpoints.py  # Administrative endpoints
├── sample_users_import.csv        # Sample CSV files for testing
├── sample_minimal_import.csv       # Minimal format sample
├── sample_small_import.csv         # Mixed status sample
├── CSV_IMPORT_GUIDE.md            # Detailed CSV format guide
├── ADMINISTRATOR_GUIDE.md         # Complete administration guide
├── FRONTEND_IMPLEMENTATION_SUMMARY.md # Frontend technical documentation
├── scim_database.db               # SQLite database (auto-created)
└── README.md                      # This file
```

## 🗄️ Database Schema

### Tables

1. **realms** - Multi-tenant realm management
   - `id`: Primary key
   - `realm_id`: Unique realm identifier (auto-generated)
   - `name`: Human-readable realm name
   - `description`: Optional realm description
   - `created_at`: Creation timestamp

2. **scim_users** - SCIM 2.0 user storage
   - `id`: Primary key
   - `user_id`: Unique user identifier (UUID)
   - `realm_id`: Foreign key to realms table
   - `schemas`: SCIM schemas (JSON)
   - `userName`: Unique username
   - `externalId`: External system identifier
   - `firstName`: User's first name
   - `surName`: User's surname
   - `displayName`: User's display name
   - `active`: Account status
   - `emails`: Email addresses (JSON)
   - `created_at`, `updated_at`: Timestamps

3. **scim_idp** - SCIM Identity Provider users
   - Same structure as scim_users for IDP-specific provisioning

4. **admin_users** - API authentication
   - `id`: Primary key
   - `username`: Admin username
   - `password_hash`: Bcrypt hashed password
   - `email`: Admin email address
   - `is_active`: Account status
   - `created_at`, `last_login`: Timestamps

## 🔧 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Modern web browser (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)

### Installation Steps

1. **Clone and Navigate**
   ```powershell
   cd c:\codes\python_projects\scim-endpoints-project\python
   ```

2. **Create Virtual Environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start the Server**
   ```powershell
   python start_server.py
   ```
   
   The server will:
   - Initialize the database with default realms and admin user
   - Start on HTTP port 8000

## 🌐 Web Frontend

### Accessing the Frontend
1. **Start the Backend**: Follow the installation steps above
2. **Open Frontend**: Navigate to `frontend/index.html` in your web browser
3. **Connect**: Use the default credentials (admin/admin123) to connect

### Frontend Features
- **🎨 Beautiful Design**: Modern, responsive interface with Apphud-inspired styling
- **🌙 Theme Support**: Light/dark themes with system preference detection
- **🔒 Secure Authentication**: Session-based authentication without localStorage password storage
- **🏢 Realm Management**: Complete realm CRUD operations with dropdown selection
- **👤 User Management**: Full user lifecycle with search, create, edit, delete operations
- **📋 Bulk Import**: Drag-and-drop CSV upload with dry-run validation
- **⚙️ Admin Panel**: System health monitoring and admin user creation
- **📱 Responsive**: Mobile-friendly design with touch-optimized controls
- **♿ Accessible**: WCAG compliant with keyboard navigation and screen reader support

### Security Features
- **Input Sanitization**: XSS prevention with proper input escaping
- **Session Storage**: Secure credential handling without localStorage
- **CSRF Protection**: Secure API request handling
- **Authentication Validation**: Server-side credential verification

## 🚀 Starting the Server

### Two Startup Scripts Available

This project provides two startup scripts with different purposes:

#### **start_server.py** (Recommended for Most Users)
- **Purpose**: Simple startup with user-friendly output
- **Location**: `python/start_server.py`
- **Features**: 
  - Shows admin credentials and usage tips
  - Handles Ctrl+C gracefully
  - No auto-reload (stable for testing)
  - Path setup handled automatically

**Usage:**
```powershell
cd python
python start_server.py
```

#### **run_server.py** (For Development)
- **Purpose**: Development-focused startup with auto-reload
- **Location**: `python/src/run_server.py`
- **Features**: 
  - Auto-reload on code changes (`reload=True`)
  - Minimal logging output
  - Designed for module execution

**Usage:**
```powershell
# Method 1: From src directory
cd python/src
python run_server.py

# Method 2: As a module (from python directory)
cd python
python -m src.run_server
```

### Quick Start Examples

**For first-time setup or general use:**
```powershell
cd python
python start_server.py
```

**For active development:**
```powershell
cd python
python -m src.run_server
```

## 🔄 Quick Database Reset

**When you need to start fresh** (corrupted data, testing, or development reset):

```powershell
# 1. Stop the server (Ctrl+C if running)
# 2. Delete the database file
cd python
Remove-Item "scim_database.db"

# 3. Restart the server (auto-recreates with defaults)
python start_server.py
```

**What this does:**
- Removes all users, realms, and admin data
- Next server start creates fresh database with default realms
- Restores default admin credentials (`admin/admin123`)
- Perfect for development testing and cleanup

**Alternative method:**
```powershell
# One-liner reset (server must be stopped first)
cd python; Remove-Item "scim_database.db" -ErrorAction SilentlyContinue; python start_server.py
```

## 🚀 Quick Start

### Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/admin/health
- **Default Admin**: username=`admin`, password=`admin123`

### Get Available Realms
```bash
curl -X GET http://localhost:8000/admin/realms \
  -H "Accept: application/json" \
  -u admin:admin123
```

### Create a SCIM User
```bash
curl -X POST http://localhost:8000/scim/v2/Realms/{realm_id}/Users \
  -H "Content-Type: application/scim+json" \
  -H "Accept: application/scim+json" \
  -u admin:admin123 \
  -d '{
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    "userName": "testuser",
    "firstName": "Test",
    "surName": "User", 
    "displayName": "Test User",
    "emails": [{"value": "test@example.com", "primary": true}],
    "active": true
  }'
```

### Get SCIM Users
```bash
curl -X GET http://localhost:8000/scim/v2/Realms/{realm_id}/Users \
  -H "Accept: application/scim+json" \
  -u admin:admin123
```

### Bulk Import Users from CSV
```bash
# Download CSV template
curl -u admin:admin123 \
  http://localhost:8000/scim/v2/Realms/{realm_id}/Users:bulk-template \
  -o bulk_import_template.csv

# Perform bulk import
curl -u admin:admin123 -X POST \
  http://localhost:8000/scim/v2/Realms/{realm_id}/Users:bulk \
  -H "Content-Type: text/csv" \
  --data-binary @your_users.csv
```

## 🌐 API Endpoints

### SCIM 2.0 User Management

- `POST /scim/v2/Realms/{realm_id}/Users` - Create user
- `GET /scim/v2/Realms/{realm_id}/Users/{user_id}` - Get user by ID
- `GET /scim/v2/Realms/{realm_id}/Users` - List users (with pagination)
- `PUT /scim/v2/Realms/{realm_id}/Users/{user_id}` - Update user
- `DELETE /scim/v2/Realms/{realm_id}/Users/{user_id}` - Delete user
- `GET /scim/v2/Realms/{realm_id}/Users/by-username/{username}` - Get by username
- `GET /scim/v2/Realms/{realm_id}/Users/by-email/{email}` - Get by email

### Bulk Import Endpoints

- `POST /scim/v2/Realms/{realm_id}/Users:bulk` - Bulk import users from CSV
- `GET /scim/v2/Realms/{realm_id}/Users:bulk-info` - Get CSV format requirements
- `GET /scim/v2/Realms/{realm_id}/Users:bulk-template` - Download CSV template
#### The realm_id should be available for all realms from a dropdown list for selection prior to uploading the csv

### Administrative Endpoints

- `POST /admin/realms` - Create new realm
- `GET /admin/realms` - List all realms
- `GET /admin/realms/{realm_id}` - Get realm details
- `POST /admin/users` - Create admin user
- `GET /admin/health` - Health check

## 📋 SCIM User Schema

```json
{
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    "userName": "smithmd",
    "externalId": "127806",
    "firstName": "Gregory",
    "surName": "Smith",
    "displayName": "Dr. Gregory Smith",
    "active": true,
    "emails": [
        {
            "value": "gregory.smith@ppth.com",
            "primary": true
        }
    ]
}
```

## 🔐 Authentication

The API uses HTTP Basic Authentication. Default credentials:
- **Username**: `admin`
- **Password**: `admin123` (⚠️ Change in production!)

## 🚀 Quick Start Example

1. **Start the server**
   ```powershell
   # For first-time users or production
   python start_server.py
   
   # For development (with auto-reload)
   python -m src.run_server
   ```

2. **Create a realm**
   ```bash
   curl -X POST "http://localhost:8000/admin/realms" \
     -u admin:admin123 \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Realm", "description": "Testing realm"}'
   ```

3. **Create a user**
   ```bash
   curl -X POST "http://localhost:8000/scim/v2/Realms/{realm_id}/Users" \
     -u admin:admin123 \
     -H "Content-Type: application/json" \
     -d '{
       "userName": "jdoe",
       "firstName": "John",
       "surName": "Doe",
       "displayName": "John Doe",
       "active": true,
       "emails": [{"value": "john.doe@example.com", "primary": true}]
     }'
   ```

4. **Bulk import multiple users**
   ```bash
   # Use the automated PowerShell workflow
   .\bulk_import_workflow.ps1
   
   # Or manually with curl
   curl -X POST "http://localhost:8000/scim/v2/Realms/{realm_id}/Users:bulk" \
     -u admin:admin123 \
     -H "Content-Type: text/csv" \
     --data-binary @sample_users_import.csv
   ```

## 🚀 Frontend Quick Start

### Using the Web Interface
1. **Start the Backend Server**
   ```powershell
   cd python
   python start_server.py
   ```

2. **Open the Frontend**
   - Navigate to `frontend/index.html` in your web browser
   - Or serve it from a local web server for better performance

3. **Connect to Your SCIM Endpoint**
   - **Base URL**: `http://localhost:8000` (default)
   - **Username**: `admin` (default)
   - **Password**: `admin123` (default)
   - Click "Connect" to authenticate

4. **Start Managing Users**
   - **Realms Tab**: View and create realms
   - **Users Tab**: Search, create, edit, and delete users  
   - **Bulk Import Tab**: Upload CSV files for bulk user creation
   - **User Schema Tab**: View complete SCIM 2.0 user schema documentation
   - **Admin Tab**: Monitor system health and create admin users

### Frontend Features Walkthrough
- **🎨 Theme Toggle**: Click the toggle switch in the top-right to switch between light and dark themes
- **🏢 Realm Selection**: Select a realm from the dropdown before managing users
- **👤 User Search**: Search by username, email, ID, or list all users
- **📋 CSV Import**: Download templates and upload CSV files with drag-and-drop
- **📄 User Schema**: Complete SCIM 2.0 user schema documentation and reference
- **⚙️ Health Monitoring**: Check system status and create additional admin users

## 📖 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Administrator Guide**: See `ADMINISTRATOR_GUIDE.md` for comprehensive bulk import documentation
- **CSV Import Guide**: See `CSV_IMPORT_GUIDE.md` for detailed CSV format requirements

## 🛠️ Development

### File Descriptions

- **`app.py`**: Main FastAPI application with middleware and route configuration
- **`models.py`**: SQLAlchemy database models and table definitions
- **`schemas.py`**: Pydantic models for request/response validation
- **`database_service.py`**: Database operations and business logic
- **`auth_service.py`**: HTTP Basic Authentication implementation
- **`init_db.py`**: Database initialization with default data
- **`run_server.py`**: Application startup script with initialization
- **`scim_endpoints.py`**: SCIM 2.0 compliant user management endpoints
- **`admin_endpoints.py`**: Administrative endpoints for realm management

### Key Features Implemented

1. ✅ **Modern Web Frontend**: Beautiful, responsive single-page application
2. ✅ **Light/Dark Themes**: Automatic system preference with manual toggle
3. ✅ **SQLite3 database** with proper SCIM schema
4. ✅ **Multi-realm support** with unique identifiers
5. ✅ **FastAPI** with comprehensive endpoints
6. ✅ **Pydantic validation** for all inputs
7. ✅ **SQLAlchemy ORM** with SQL injection protection
8. ✅ **PEP 8 compliant code** with type hints
9. ✅ **Unique user ID generation** with multiple lookup options
10. ✅ **Comprehensive logging** and error handling
11. ✅ **Clean project structure** with no redundant files
12. ✅ **Bulk CSV import** with validation and error reporting
13. ✅ **PowerShell automation** workflow for testing environments
14. ✅ **Security-first frontend** with XSS protection and secure storage

## 🔒 Security Features

### Backend Security
- **Password Hashing**: Bcrypt with salt for admin passwords
- **SQL Injection Protection**: SQLAlchemy ORM parameterized queries
- **Input Validation**: Pydantic schemas for all API inputs
- **Authentication**: HTTP Basic Auth for all endpoints

### Frontend Security Features

- **🔐 Secure Authentication**: HTTP Basic Auth with session management
- **🚫 No Password Storage**: Passwords never stored in localStorage  
- **🛡️ Input Sanitization**: XSS prevention with proper escaping
- **🔒 Session Storage**: Secure credential handling
- **🎨 Light/Dark Themes**: System preference detection with manual override
- **🔑 Password Management**: Secure password change functionality

### Key Frontend Capabilities

- **Complete SCIM API Integration**: All endpoints covered with intuitive forms
- **Real-time User Management**: Create, read, update, delete users seamlessly  
- **Advanced Search**: Find users by username, email, or ID
- **Bulk Operations**: CSV import with drag-and-drop support
- **Realm Management**: Multi-tenant support with realm selection
- **Admin Functions**: Health monitoring and user creation
- **Password Security**: Built-in password change with validation
- **Mobile Responsive**: Works perfectly on all device sizes

## 📝 Work Summary

This project implements a complete SCIM 2.0 compliant API following modern provisioning standards. Key accomplishments:

- Built a robust multi-tenant architecture with realm isolation
- Implemented comprehensive SCIM 2.0 user management capabilities
- Created secure authentication and authorization mechanisms
- Developed type-safe, well-documented Python code following best practices
- Established proper database design with SQLAlchemy ORM
- Provided extensive API documentation and developer tools

The implementation is stable for testing with proper error handling, logging, and security measures in place.

## 🧪 Testing

### Comprehensive Test Suite

The project includes multiple test suites that verify all SCIM 2.0 and bulk import functionality:

**`test_scim_api.py`** - Complete SCIM 2.0 API test suite featuring:
- ✅ **12 Comprehensive Tests** covering all functionality
- 🚀 Health check and server connectivity
- 🏢 Multi-realm support and functionality  
- 👤 Complete SCIM user CRUD operations
- 📧 **Email update testing** including single and multiple email scenarios
- 🔍 User lookup by username and email
- 🧹 Proper test cleanup and resource management

**`test_bulk_import.py`** - Comprehensive bulk CSV import test suite featuring:
- ✅ **10 Comprehensive Tests** covering all bulk import scenarios
- 📋 Realm discovery and selection workflow
- 📄 CSV template download and validation
- 🔍 Dry run validation testing
- 📊 Actual bulk import with multiple users
- ⚠️ Duplicate detection and error handling
- 🗂️ Large file processing (hundreds of users)
- 🧹 Automated user cleanup after testing

### Test Coverage

✅ **All 12 Tests Passing** - Complete test suite validates:
1. Health Check - Server connectivity and status
2. Realm Listing - Multi-tenant realm functionality
3. User Creation - SCIM compliant user provisioning
4. User Retrieval - Individual user lookup by ID
5. User Update - SCIM user modification
6. User Listing - Paginated user collections
7. Username Lookup - User search by username
8. User Deletion - Proper user removal
9. Deletion Verification - Confirm user removal
10. **Email Test User Creation** - Setup for email testing
11. **Single Email Update** - PUT request email modification
12. **Multiple Email Update** - Complex email scenarios with primary/secondary

### Running Tests

```powershell
# Run the complete SCIM API test suite
python test_scim_api.py

# Run the bulk import test suite  
python test_bulk_import.py

# Use PowerShell automation for interactive bulk import testing
.\bulk_import_workflow.ps1
```

**Sample Output:**
```
🚀 SCIM 2.0 Endpoints Test Suite
==================================================
✅ All 12 tests completed successfully!
```

## 🔧 Recent Fixes

### Email Update Issue Resolution
**Issue**: PUT requests for updating user emails were failing with 500 Internal Server Error.

**Root Cause**: Syntax error in `database_service.py` where a docstring and code were merged on the same line.

**Fix Applied**: 
- Corrected line formatting in the `update_scim_user` method
- Verified proper email handling for both single and multiple email scenarios
- Enhanced error handling for email validation

**Verification**: All email update scenarios now pass comprehensive testing.

---

## 📋 Implementation Summary

This project implements a complete SCIM 2.0 compliant system with:

### 🖥️ **Frontend Application**
- **Single-Page Application**: Modern, responsive web interface
- **Beautiful Design**: Apphud-inspired styling with professional appearance
- **Theme Support**: Light/dark themes with system preference detection
- **Complete API Integration**: All SCIM endpoints accessible through UI
- **Security Features**: XSS protection, secure authentication, session management
- **Mobile-Friendly**: Responsive design optimized for all devices
- **Accessibility**: WCAG compliant with keyboard navigation support

### 🔧 **Backend API**
- **SCIM 2.0 Compliance**: Full RFC 7643 implementation
- **Multi-Realm Architecture**: Isolated tenant environments
- **Bulk Import System**: CSV processing with validation and error reporting
- **PowerShell Automation**: Scripted workflows for testing environments
- **Comprehensive Security**: Authentication, input validation, SQL injection protection
- **Performance Optimized**: Efficient database operations with proper indexing

### 📚 **Documentation**
- **README.md**: Main project documentation with setup and usage
- **ADMINISTRATOR_GUIDE.md**: Comprehensive administration guide
- **CSV_IMPORT_GUIDE.md**: Detailed CSV format documentation
- **IMPLEMENTATION_SUMMARY.md**: Backend technical implementation details
- **FRONTEND_IMPLEMENTATION_SUMMARY.md**: Frontend architecture and security documentation

### 🧪 **Testing & Quality**
- **Automated Testing**: Complete test suite with 12 SCIM API tests
- **Bulk Import Testing**: Dedicated test suite for CSV operations
- **Error Handling**: Comprehensive error management and recovery
- **Code Quality**: PEP 8 compliance with full type hints
