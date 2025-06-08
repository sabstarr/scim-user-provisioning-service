"""
Authentication service for SCIM 2.0 endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from .models import get_db
from .database_service import DatabaseService

security = HTTPBasic()


def authenticate_admin(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    """
    Authenticate admin user using HTTP Basic Auth.
    Returns username if authentication is successful.
    """
    admin_user = DatabaseService.get_admin_user(db, credentials.username)
    
    if not admin_user or not admin_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    if not DatabaseService.verify_admin_password(credentials.password, admin_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Update last login
    admin_user.last_login = datetime.utcnow()
    db.commit()
    
    return credentials.username


def get_current_admin(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    """
    Get current authenticated admin user.
    This is an alias for authenticate_admin for better readability.
    """
    return authenticate_admin(credentials, db)
