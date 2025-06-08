"""
SCIM 2.0 Endpoints for user provisioning.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from ..models import get_db
from ..schemas import (
    SCIMUserCreate, SCIMUserUpdate, SCIMUserResponse, SCIMUserListResponse,
    ErrorResponse, SuccessResponse, BulkImportResponse, BulkImportRequest
)
from ..database_service import DatabaseService
from ..auth_service import get_current_admin
from ..bulk_import_service import BulkImportService

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


@router.post(
    "/scim/v2/Realms/{realm_id}/Users/bulk-import",
    response_model=BulkImportResponse,
    status_code=status.HTTP_200_OK,
    tags=["SCIM Bulk Operations"]
)
async def bulk_import_users(
    realm_id: str,
    file: UploadFile = File(..., description="CSV file containing user data"),
    dry_run: bool = Form(False, description="Perform validation only without creating users"),
    skip_duplicates: bool = Form(True, description="Skip users that already exist"),
    continue_on_error: bool = Form(True, description="Continue processing if individual users fail"),
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
) -> BulkImportResponse:
    """
    Bulk import users from CSV file.
    
    CSV Format:
    - Required columns: userName, firstName, surName, email
    - Optional columns: displayName, secondaryEmail, externalId, active
    - Maximum file size: 5MB
    - Maximum users per import: 1000
    
    Args:
        realm_id: Unique realm identifier
        file: CSV file with user data
        dry_run: If true, validate only without creating users
        skip_duplicates: If true, skip users that already exist
        continue_on_error: If true, continue processing even if some users fail
        db: Database session
        current_admin: Authenticated admin username
    
    Returns:
        Detailed import results with success/failure counts and individual user results
    """
    logger.info(f"Bulk import requested for realm {realm_id} by admin {current_admin}")
    
    # Verify realm exists
    realm = DatabaseService.get_realm_by_id(db, realm_id)
    if not realm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Realm with ID '{realm_id}' not found"
        )
    
    # Create import parameters
    import_params = BulkImportRequest(
        dry_run=dry_run,
        skip_duplicates=skip_duplicates,
        continue_on_error=continue_on_error
    )
    
    # Process the bulk import
    try:
        result = await BulkImportService.process_bulk_import(
            file=file,
            realm_id=realm_id,
            db=db,
            admin_username=current_admin,
            params=import_params
        )
        
        logger.info(f"Bulk import completed: {result.successful_imports} successful, "
                   f"{result.failed_imports} failed, {result.skipped_imports} skipped")
        
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error in bulk import: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk import failed: {str(e)}"
        )


@router.get(
    "/scim/v2/Realms/{realm_id}/Users/bulk-import/template",
    response_class=Response,
    tags=["SCIM Bulk Operations"]
)
async def download_csv_template(
    realm_id: str,
    current_admin: str = Depends(get_current_admin)
) -> Response:
    """
    Download a CSV template for bulk user import.
    
    Args:
        realm_id: Unique realm identifier (for authorization)
        current_admin: Authenticated admin username
    
    Returns:
        CSV template file with example data and proper headers
    """
    logger.info(f"CSV template requested for realm {realm_id} by admin {current_admin}")
    
    try:
        csv_content = BulkImportService.generate_csv_template()
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=scim_users_template.csv"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating CSV template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CSV template: {str(e)}"
        )


@router.get(
    "/scim/v2/Realms/{realm_id}/Users/bulk-import/status",
    response_model=SuccessResponse,
    tags=["SCIM Bulk Operations"]
)
async def get_bulk_import_info(
    realm_id: str,
    current_admin: str = Depends(get_current_admin)
) -> SuccessResponse:
    """
    Get information about bulk import capabilities and requirements.
    
    Args:
        realm_id: Unique realm identifier
        current_admin: Authenticated admin username
    
    Returns:
        Information about bulk import features and limitations
    """
    logger.info(f"Bulk import info requested for realm {realm_id} by admin {current_admin}")
    
    return SuccessResponse(
        message="Bulk import service is available",
        data={
            "max_file_size_mb": BulkImportService.MAX_FILE_SIZE / (1024 * 1024),
            "max_users_per_import": BulkImportService.MAX_USERS_PER_IMPORT,
            "required_columns": BulkImportService.REQUIRED_COLUMNS,
            "optional_columns": BulkImportService.OPTIONAL_COLUMNS,
            "supported_file_formats": ["CSV"],
            "features": {
                "dry_run": "Validate CSV without creating users",
                "skip_duplicates": "Skip users that already exist",
                "continue_on_error": "Continue processing even if some users fail",
                "detailed_results": "Get detailed success/failure information for each user"
            }
        }
    )
