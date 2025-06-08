"""
Pydantic schemas for SCIM 2.0 endpoints validation.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EmailSchema(BaseModel):
    """SCIM Email schema."""
    value: EmailStr = Field(..., description="Email address")
    primary: bool = Field(default=False, description="Primary email indicator")


class SCIMUserCreate(BaseModel):
    """Schema for creating SCIM users."""
    schemas: List[str] = Field(
        default=["urn:ietf:params:scim:schemas:core:2.0:User"],
        description="SCIM schemas"
    )
    userName: str = Field(..., min_length=1, max_length=100, description="Username")
    externalId: Optional[str] = Field(None, max_length=100, description="External ID")
    firstName: str = Field(..., min_length=1, max_length=100, description="First name")
    surName: str = Field(..., min_length=1, max_length=100, description="Surname")
    displayName: str = Field(..., min_length=1, max_length=200, description="Display name")
    active: bool = Field(default=True, description="Active status")
    emails: List[EmailSchema] = Field(..., min_items=1, description="Email addresses")

    @validator('emails')
    def validate_primary_email(cls, v):
        """Ensure at least one primary email exists."""
        if not any(email.primary for email in v):
            v[0].primary = True  # Set first email as primary if none specified
        return v

    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SCIMUserUpdate(BaseModel):
    """Schema for updating SCIM users."""
    schemas: Optional[List[str]] = Field(None, description="SCIM schemas")
    userName: Optional[str] = Field(None, min_length=1, max_length=100, description="Username")
    externalId: Optional[str] = Field(None, max_length=100, description="External ID")
    firstName: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    surName: Optional[str] = Field(None, min_length=1, max_length=100, description="Surname")
    displayName: Optional[str] = Field(None, min_length=1, max_length=200, description="Display name")
    active: Optional[bool] = Field(None, description="Active status")
    emails: Optional[List[EmailSchema]] = Field(None, description="Email addresses")

    @validator('emails')
    def validate_primary_email(cls, v):
        """Ensure at least one primary email exists if emails provided."""
        if v and not any(email.primary for email in v):
            v[0].primary = True
        return v


class SCIMUserResponse(BaseModel):
    """Schema for SCIM user response."""
    id: str = Field(..., description="User ID")
    schemas: List[str] = Field(..., description="SCIM schemas")
    userName: str = Field(..., description="Username")
    externalId: Optional[str] = Field(None, description="External ID")
    firstName: str = Field(..., description="First name")
    surName: str = Field(..., description="Surname")
    displayName: str = Field(..., description="Display name")
    active: bool = Field(..., description="Active status")
    emails: List[EmailSchema] = Field(..., description="Email addresses")
    meta: Dict[str, Any] = Field(..., description="Metadata")

    class Config:
        """Pydantic config."""
        from_attributes = True


class SCIMUserListResponse(BaseModel):
    """Schema for SCIM user list response."""
    schemas: List[str] = Field(
        default=["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        description="SCIM schemas"
    )
    totalResults: int = Field(..., description="Total number of results")
    startIndex: int = Field(default=1, description="Start index")
    itemsPerPage: int = Field(..., description="Items per page")
    Resources: List[SCIMUserResponse] = Field(..., description="User resources")


class RealmCreate(BaseModel):
    """Schema for creating realms."""
    name: str = Field(..., min_length=1, max_length=100, description="Realm name")
    description: Optional[str] = Field(None, description="Realm description")


class RealmResponse(BaseModel):
    """Schema for realm response."""
    id: int = Field(..., description="Realm database ID")
    realm_id: str = Field(..., description="Realm identifier")
    name: str = Field(..., description="Realm name")
    description: Optional[str] = Field(None, description="Realm description")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class AdminUserCreate(BaseModel):
    """Schema for creating admin users."""
    username: str = Field(..., min_length=1, max_length=100, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    email: EmailStr = Field(..., description="Email address")


class AdminUserResponse(BaseModel):
    """Schema for admin user response."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    schemas: List[str] = Field(
        default=["urn:ietf:params:scim:api:messages:2.0:Error"],
        description="Error schema"
    )
    detail: str = Field(..., description="Error detail")
    status: str = Field(..., description="HTTP status code")


class SuccessResponse(BaseModel):
    """Schema for success responses."""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class BulkImportStatus(str, Enum):
    """Status enum for bulk import operations."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"


class BulkUserResult(BaseModel):
    """Result for a single user in bulk import."""
    row_number: int = Field(..., description="Row number in CSV file")
    userName: Optional[str] = Field(None, description="Username from CSV")
    status: str = Field(..., description="Import status (success/error)")
    user_id: Optional[str] = Field(None, description="Created user ID if successful")
    message: str = Field(..., description="Success or error message")
    errors: Optional[List[str]] = Field(None, description="Validation errors if any")


class BulkImportRequest(BaseModel):
    """Schema for bulk import request parameters."""
    dry_run: bool = Field(default=False, description="Perform validation only without creating users")
    skip_duplicates: bool = Field(default=True, description="Skip users that already exist")
    continue_on_error: bool = Field(default=True, description="Continue processing if individual users fail")


class BulkImportResponse(BaseModel):
    """Schema for bulk import response."""
    status: BulkImportStatus = Field(..., description="Overall import status")
    total_rows: int = Field(..., description="Total number of rows processed")
    successful_imports: int = Field(..., description="Number of successfully imported users")
    failed_imports: int = Field(..., description="Number of failed imports")
    skipped_imports: int = Field(..., description="Number of skipped imports (duplicates)")
    processing_time_seconds: float = Field(..., description="Total processing time in seconds")
    results: List[BulkUserResult] = Field(..., description="Detailed results for each user")
    errors: Optional[List[str]] = Field(None, description="General processing errors")
    csv_validation_errors: Optional[List[str]] = Field(None, description="CSV format validation errors")


class CSVUserRow(BaseModel):
    """Schema for validating CSV user rows."""
    userName: str = Field(..., description="Username (required)")
    firstName: str = Field(..., description="First name (required)")
    surName: str = Field(..., description="Surname (required)")
    displayName: Optional[str] = Field(None, description="Display name (optional, auto-generated if not provided)")
    email: EmailStr = Field(..., description="Primary email address (required)")
    secondaryEmail: Optional[EmailStr] = Field(None, description="Secondary email address (optional)")
    externalId: Optional[str] = Field(None, description="External ID (optional)")
    active: Optional[bool] = Field(default=True, description="Active status (optional, defaults to True)")

    @validator('displayName', always=True)
    def generate_display_name(cls, v, values):
        """Auto-generate display name if not provided."""
        if not v and 'firstName' in values and 'surName' in values:
            return f"{values['firstName']} {values['surName']}"
        return v
