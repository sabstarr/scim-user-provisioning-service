# SCIM Bulk User Import CSV Format Guide

## 📋 Overview

The SCIM 2.0 Endpoints service supports bulk user import via CSV files. This guide explains the required format and provides examples.

## 📝 CSV Format Requirements

### Required Columns
These columns **must** be present in your CSV file:

| Column | Description | Example | Required |
|--------|-------------|---------|----------|
| `userName` | Unique username for the user | `john.doe` | ✅ |
| `firstName` | User's first name | `John` | ✅ |
| `surName` | User's last name/surname | `Doe` | ✅ |
| `email` | Primary email address | `john.doe@company.com` | ✅ |

### Optional Columns
These columns are optional but recommended:

| Column | Description | Example | Default |
|--------|-------------|---------|---------|
| `displayName` | Display name shown in UI | `John Doe` | Auto-generated from firstName + surName |
| `secondaryEmail` | Additional email address | `j.doe@personal.com` | None |
| `externalId` | External system identifier | `EMP001` | None |
| `active` | Account status | `true`, `false`, `yes`, `no`, `1`, `0`, `active`, `inactive` | `true` |

## 📏 File Constraints

- **Maximum file size**: 5MB
- **Maximum users per import**: 1,000 users
- **File encoding**: UTF-8 (recommended)
- **File extension**: Must be `.csv`
- **Column headers**: Must be in the first row

## 📊 Sample CSV Files

### 1. Full Example (sample_users_import.csv)
Complete example with all columns:

```csv
userName,firstName,surName,email,displayName,secondaryEmail,externalId,active
john.doe,John,Doe,john.doe@company.com,John Doe,j.doe@personal.com,EMP001,true
jane.smith,Jane,Smith,jane.smith@company.com,Jane Smith,,EMP002,true
```

### 2. Minimal Example (sample_minimal_import.csv)
Using only required columns:

```csv
userName,firstName,surName,email
testuser1,Test,User1,testuser1@example.com
testuser2,Test,User2,testuser2@example.com
```

### 3. Mixed Status Example (sample_small_import.csv)
Showing different active status formats:

```csv
userName,firstName,surName,email,displayName,secondaryEmail,externalId,active
alice.johnson,Alice,Johnson,alice.johnson@example.com,Alice Johnson,,TEMP001,true
bob.smith,Bob,Smith,bob.smith@example.com,Robert Smith,bob.personal@gmail.com,TEMP002,false
charlie.brown,Charlie,Brown,charlie.brown@example.com,,charlie.b@yahoo.com,TEMP003,inactive
```

## 🔧 Data Validation Rules

### Username Requirements
- Must be unique within the realm
- Cannot be empty
- Recommended: Use lowercase with dots/underscores

### Email Requirements
- Must be valid email format
- Primary email must be unique within the realm
- Secondary email can be duplicate or empty

### Active Status Values
The following values are accepted for the `active` column:

**Active (True)**:
- `true`, `True`, `TRUE`
- `1`
- `yes`, `Yes`, `YES`
- `active`, `Active`, `ACTIVE`

**Inactive (False)**:
- `false`, `False`, `FALSE`
- `0`
- `no`, `No`, `NO`
- `inactive`, `Inactive`, `INACTIVE`

**Default**: If not specified or invalid value, defaults to `true` (active)

## 🚀 Using the Bulk Import API

### Endpoint
```
POST /scim/v2/Realms/{realm_id}/Users/bulk-import
```

### Authentication
HTTP Basic Auth required:
- Username: `admin`
- Password: `admin123` (change in production!)

### Request Format
- **Content-Type**: `multipart/form-data`
- **File Parameter**: `file`
- **Optional Parameters**: 
  - `dry_run` (boolean): Validate without importing
  - `stop_on_first_error` (boolean): Stop processing on first error

### Example Request (curl)
```bash
curl -u admin:admin123 \
  -X POST \
  -F "file=@sample_users_import.csv" \
  -F "dry_run=false" \
  -F "stop_on_first_error=false" \
  http://localhost:8000/scim/v2/Realms/{realm_id}/Users/bulk-import
```

### Example Request (PowerShell)
```powershell
$headers = @{
    'Authorization' = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('admin:admin123'))
}

$form = @{
    file = Get-Item "sample_users_import.csv"
    dry_run = "false"
    stop_on_first_error = "false"
}

Invoke-RestMethod -Uri "http://localhost:8000/scim/v2/Realms/{realm_id}/Users/bulk-import" -Method Post -Headers $headers -Form $form
```

## 📊 Response Format

### Success Response
```json
{
    "status": "completed",
    "total_rows": 20,
    "successful_imports": 18,
    "failed_imports": 2,
    "validation_errors": 0,
    "processing_time_seconds": 2.45,
    "results": [
        {
            "row_number": 1,
            "status": "success",
            "user_id": "c40157f5-7405-421b-8a72-6171de4a524b",
            "username": "john.doe",
            "message": "User created successfully"
        },
        {
            "row_number": 5,
            "status": "error",
            "username": "duplicate.user",
            "error": "User with username 'duplicate.user' already exists"
        }
    ]
}
```

## ⚠️ Common Issues and Solutions

### 1. File Format Issues
**Problem**: "CSV parsing error" or "Unable to decode CSV file"
**Solutions**:
- Save file as CSV with UTF-8 encoding
- Ensure proper comma separation
- Remove any special characters in headers

### 2. Missing Required Columns
**Problem**: "Missing required columns: firstName, surName"
**Solutions**:
- Ensure all required columns are present
- Check spelling of column headers
- Remove any extra spaces in headers

### 3. Duplicate Users
**Problem**: "User with username 'john.doe' already exists"
**Solutions**:
- Use unique usernames in CSV
- Check existing users before import
- Use `dry_run=true` to validate first

### 4. Email Format Issues
**Problem**: "Invalid email format"
**Solutions**:
- Ensure emails follow standard format (name@domain.com)
- Remove any extra spaces
- Check for special characters

### 5. File Size Limits
**Problem**: "File size exceeds maximum allowed size"
**Solutions**:
- Split large files into smaller chunks (max 1,000 users)
- Compress unnecessary columns
- Remove empty rows

## 🔍 Testing Your CSV

Before importing production data:

1. **Use Dry Run Mode**: Set `dry_run=true` to validate without creating users
2. **Test with Small File**: Start with 2-3 users to verify format
3. **Check Response**: Review all error messages and warnings
4. **Verify Required Columns**: Ensure all required fields are present

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **SCIM 2.0 Specification**: RFC 7643
- **Administrator Guide**: See ADMINISTRATOR_GUIDE.md
- **Sample CSV Files**: Available in project root directory
