"""
Admin endpoints for realm and user management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from ..models import get_db
from ..schemas import (
    RealmCreate, RealmResponse, AdminUserCreate, AdminUserResponse,
    SuccessResponse
)
from ..database_service import DatabaseService
from ..auth_service import get_current_admin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/admin/realms",
    response_model=RealmResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Admin - Realms"]
)
async def create_realm(
    realm_data: RealmCreate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> RealmResponse:
    """
    Create a new realm for SCIM endpoint isolation.
    
    Args:
        realm_data: Realm creation data
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        Created realm data
    """
    logger.info(f"Creating realm '{realm_data.name}' by admin {current_admin}")
    
    try:
        realm = DatabaseService.create_realm(db, realm_data)
        logger.info(f"Successfully created realm {realm.realm_id}")
        return RealmResponse.model_validate(realm)
    except Exception as e:
        logger.error(f"Error creating realm: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/admin/realms",
    response_model=List[RealmResponse],
    tags=["Admin - Realms"]
)
async def list_realms(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> List[RealmResponse]:
    """
    List all available realms.
    
    Args:
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        List of all realms
    """
    logger.info(f"Listing realms by admin {current_admin}")
    
    realms = DatabaseService.get_all_realms(db)
    return [RealmResponse.model_validate(realm) for realm in realms]


@router.get(
    "/admin/realms/{realm_id}",
    response_model=RealmResponse,
    tags=["Admin - Realms"]
)
async def get_realm(
    realm_id: str,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> RealmResponse:
    """
    Get a specific realm by ID.
    
    Args:
        realm_id: Unique realm identifier
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        Realm data
    """
    logger.info(f"Getting realm {realm_id} by admin {current_admin}")
    
    realm = DatabaseService.get_realm_by_id(db, realm_id)
    if not realm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Realm with ID '{realm_id}' not found"
        )
    
    return RealmResponse.model_validate(realm)


@router.post(
    "/admin/users",
    response_model=AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Admin - Users"]
)
async def create_admin_user(
    admin_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> AdminUserResponse:
    """
    Create a new admin user.
    
    Args:
        admin_data: Admin user creation data
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        Created admin user data
    """
    logger.info(f"Creating admin user '{admin_data.username}' by admin {current_admin}")
    
    try:
        # Check if admin already exists
        existing_admin = DatabaseService.get_admin_user(db, admin_data.username)
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Admin user with username '{admin_data.username}' already exists"
            )
        
        admin_user = DatabaseService.create_admin_user(db, admin_data)
        logger.info(f"Successfully created admin user {admin_user.username}")
        return AdminUserResponse.model_validate(admin_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(
    "/admin/health",
    response_model=SuccessResponse,
    tags=["Admin - Health"]
)
async def health_check(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> SuccessResponse:
    """
    Health check endpoint for admin access.
    
    Args:
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        Health status
    """
    logger.info(f"Health check by admin {current_admin}")
    
    return SuccessResponse(
        message="SCIM endpoints are healthy",
        data={"admin": current_admin, "status": "active"}
    )
