"""
SCIM 2.0 Endpoints for user provisioning.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from ..models import get_db
from ..schemas import (
    SCIMUserCreate, SCIMUserUpdate, SCIMUserResponse, SCIMUserListResponse,
    ErrorResponse, SuccessResponse
)
from ..database_service import DatabaseService
from ..auth_service import get_current_admin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/scim/v2/Realms/{realm_id}/Users",
    response_model=SCIMUserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["SCIM Users"]
)
async def create_user(
    realm_id: str,
    user_data: SCIMUserCreate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> SCIMUserResponse:
    """
    Create a new SCIM user in the specified realm.
    
    Args:
        realm_id: Unique realm identifier
        user_data: User data following SCIM 2.0 schema
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        Created user data with SCIM response format
    """
    try:
        logger.info(f"Creating user {user_data.userName} in realm {realm_id} by admin {current_admin}")
        
        # Check if user already exists
        existing_user = DatabaseService.get_scim_user_by_username(db, user_data.userName, realm_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with username '{user_data.userName}' already exists in realm '{realm_id}'"
            )
        
        # Create user
        user = DatabaseService.create_scim_user(db, user_data, realm_id)
        user_dict = DatabaseService.user_to_dict(user)
        
        logger.info(f"Successfully created user {user.userName} with ID {user.user_id}")
        return SCIMUserResponse(**user_dict)
        
    except ValueError as e:
        logger.error(f"ValueError creating user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/scim/v2/Realms/{realm_id}/Users/{user_id}",
    response_model=SCIMUserResponse,
    tags=["SCIM Users"]
)
async def get_user(
    realm_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> SCIMUserResponse:
    """
    Get a specific SCIM user by ID.
    
    Args:
        realm_id: Unique realm identifier
        user_id: Unique user identifier
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        User data with SCIM response format
    """
    logger.info(f"Getting user {user_id} from realm {realm_id} by admin {current_admin}")
    
    user = DatabaseService.get_scim_user_by_id(db, user_id, realm_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found in realm '{realm_id}'"
        )
    
    user_dict = DatabaseService.user_to_dict(user)
    return SCIMUserResponse(**user_dict)


@router.get(
    "/scim/v2/Realms/{realm_id}/Users",
    response_model=SCIMUserListResponse,
    tags=["SCIM Users"]
)
async def list_users(
    realm_id: str,
    startIndex: int = Query(1, ge=1, description="Start index for pagination"),
    count: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    filter: Optional[str] = Query(None, description="Filter query"),
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> SCIMUserListResponse:
    """
    List SCIM users with pagination and filtering.
    
    Args:
        realm_id: Unique realm identifier
        startIndex: Start index for pagination (1-based)
        count: Number of users to return
        filter: Optional filter query
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        List of users with pagination metadata
    """
    logger.info(f"Listing users from realm {realm_id} by admin {current_admin}")
    
    users, total_count = DatabaseService.get_scim_users(
        db, realm_id, startIndex, count, filter
    )
    
    user_resources = [
        SCIMUserResponse(**DatabaseService.user_to_dict(user)) 
        for user in users
    ]
    
    return SCIMUserListResponse(
        totalResults=total_count,
        startIndex=startIndex,
        itemsPerPage=len(user_resources),
        Resources=user_resources
    )


@router.put(
    "/scim/v2/Realms/{realm_id}/Users/{user_id}",
    response_model=SCIMUserResponse,
    tags=["SCIM Users"]
)
async def update_user(
    realm_id: str,
    user_id: str,
    user_data: SCIMUserUpdate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> SCIMUserResponse:
    """
    Update a SCIM user.
    
    Args:
        realm_id: Unique realm identifier
        user_id: Unique user identifier
        user_data: Updated user data
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        Updated user data with SCIM response format
    """
    logger.info(f"Updating user {user_id} in realm {realm_id} by admin {current_admin}")
    
    user = DatabaseService.update_scim_user(db, user_id, realm_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found in realm '{realm_id}'"
        )
    
    user_dict = DatabaseService.user_to_dict(user)
    return SCIMUserResponse(**user_dict)


@router.delete(
    "/scim/v2/Realms/{realm_id}/Users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["SCIM Users"]
)
async def delete_user(
    realm_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> None:
    """
    Delete a SCIM user.
    
    Args:
        realm_id: Unique realm identifier
        user_id: Unique user identifier
        db: Database session
        current_admin: Authenticated admin username
    """
    logger.info(f"Deleting user {user_id} from realm {realm_id} by admin {current_admin}")
    
    deleted = DatabaseService.delete_scim_user(db, user_id, realm_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found in realm '{realm_id}'"
        )


@router.get(
    "/scim/v2/Realms/{realm_id}/Users/by-username/{username}",
    response_model=SCIMUserResponse,
    tags=["SCIM Users"]
)
async def get_user_by_username(
    realm_id: str,
    username: str,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> SCIMUserResponse:
    """
    Get a SCIM user by username.
    
    Args:
        realm_id: Unique realm identifier
        username: Username to search for
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        User data with SCIM response format
    """
    logger.info(f"Getting user by username {username} from realm {realm_id} by admin {current_admin}")
    
    user = DatabaseService.get_scim_user_by_username(db, username, realm_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username '{username}' not found in realm '{realm_id}'"
        )
    
    user_dict = DatabaseService.user_to_dict(user)
    return SCIMUserResponse(**user_dict)


@router.get(
    "/scim/v2/Realms/{realm_id}/Users/by-email/{email}",
    response_model=SCIMUserResponse,
    tags=["SCIM Users"]
)
async def get_user_by_email(
    realm_id: str,
    email: str,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> SCIMUserResponse:
    """
    Get a SCIM user by email address.
    
    Args:
        realm_id: Unique realm identifier
        email: Email address to search for
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        User data with SCIM response format
    """
    logger.info(f"Getting user by email {email} from realm {realm_id} by admin {current_admin}")
    
    user = DatabaseService.get_scim_user_by_email(db, email, realm_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{email}' not found in realm '{realm_id}'"
        )
    
    user_dict = DatabaseService.user_to_dict(user)
    return SCIMUserResponse(**user_dict)
