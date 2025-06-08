"""
Pydantic schemas for SCIM 2.0 endpoints validation.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


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
